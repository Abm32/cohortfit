"""Audit orchestrator — the only module that knows the full Tier 0 pipeline.

Claude fills ``Protocol``; everything in this module is deterministic arithmetic
on pinned fixtures and pgx-core tables. No LLM, no network when ``offline=True``.
"""

from __future__ import annotations

import json
from pathlib import Path

from anukriti_pgx_core.phenotype.recommendation_level import level_for

from .ancestry import apply_ancestry_defaults
from .cohort import blend_allele_frequencies, cohort_ancestry_mix, population_coverage
from .frequencies import FixtureError, load_gene_frequencies, load_gene_provenance
from .models import AuditReport, GeneDrugFinding, Protocol, SiteFinding, Tier
from .pgx import cohort_phenotype_distribution, table_citation
from .rules import normalize_drug, resolve_gene, screening_gap
from .sites import site_metabolic_burden


def load_protocol(path: Path | str) -> Protocol:
    """Load and validate a protocol JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Protocol.model_validate(data)


def audit_protocol(protocol: Protocol, *, offline: bool = True) -> AuditReport:
    """Run Tier 0 genomic feasibility audit on a structured protocol.

    Pipeline per drug:
        resolve gene → load frequencies → blend ancestry → HWE → phenotype table
        → screening-gap rule → per-site metabolic burden

    Args:
        protocol: Validated protocol (Claude extraction output or pinned fixture).
        offline: Must be True; loads pinned fixtures only.

    Returns:
        AuditReport with findings, site_findings, and data_sources provenance.
    """
    if not offline:
        raise FixtureError("Live audit is not supported; use offline=True")

    # Fill site ancestry from country priors when the protocol omits it, so a
    # hand-authored fixture behaves like extractor output rather than silently
    # producing no findings.
    protocol = apply_ancestry_defaults(protocol)

    data_sources: list[str] = []
    findings: list[GeneDrugFinding] = []
    site_findings: list[SiteFinding] = []
    warnings: list[str] = []

    sites_without_ancestry = [s.name for s in protocol.sites if not s.ancestry_mix]
    if sites_without_ancestry:
        warnings.append(
            "No ancestry_mix for site(s) "
            + ", ".join(sites_without_ancestry)
            + " and no country prior available — these sites are excluded from "
            "the cohort distribution."
        )
    if not protocol.sites:
        warnings.append(
            "Protocol declares no sites; cohort ancestry cannot be computed and "
            "no Tier 0 distribution was produced."
        )

    for drug_regimen in protocol.drugs:
        drug = drug_regimen.drug
        gene = resolve_gene(drug)
        if gene is None:
            continue

        per_pop_freqs = load_gene_frequencies(gene, offline=offline)
        prov = load_gene_provenance(gene)
        meta = prov.get("meta", {})
        query_date = meta.get("query_date", "unknown")
        gnomad_version = meta.get("gnomad_version", "unknown")
        dataset = meta.get("gnomad_dataset")
        dataset_label = f"{gnomad_version} {dataset}" if dataset else gnomad_version
        data_sources.append(
            f"gnomAD {dataset_label} allele frequencies for {gene} "
            f"(query_date={query_date}, fixture=frequencies/{gene.lower()}.json)"
        )

        # An unreconciled disagreement between the pinned value and other
        # published sources must reach the reader; a fixture that records the
        # conflict but never surfaces it is no better than one that hides it.
        for disc in prov.get("known_discrepancies", []):
            if str(disc.get("status", "")).upper().startswith("RESOLVED"):
                continue
            warnings.append(
                f"{gene} {disc.get('allele', '?')} ({disc.get('population', '?')}): "
                f"pinned {disc.get('pinned')} conflicts with other published "
                f"sources. {disc.get('direction_of_error', '')} "
                "See fixtures/frequencies/"
                f"{gene.lower()}.json → _meta.known_discrepancies."
            )

        # Cohort-wide distribution (enrolment-weighted ancestry mix).
        mix = cohort_ancestry_mix(protocol.sites)
        coverage = population_coverage(per_pop_freqs, mix)
        blended = blend_allele_frequencies(per_pop_freqs, mix)
        if not blended:
            warnings.append(
                f"{gene} × {drug}: no pinned allele frequencies for any declared "
                f"ancestry group ({', '.join(sorted(mix)) or 'none declared'}); "
                "no distribution computed. This is a data-coverage gap, not a "
                "finding of no risk."
            )
            continue

        dist, table = cohort_phenotype_distribution(
            gene, blended, protocol.total_planned_n
        )
        data_sources.append(table_citation(table))

        verdict, missing_exclusion, citations = screening_gap(protocol, drug, gene)
        cpic_level = level_for(gene, normalize_drug(drug)) or None

        notes: list[str] = []
        if coverage.dropped:
            dropped_desc = ", ".join(
                f"{pop} {weight:.0%}" for pop, weight in sorted(coverage.dropped.items())
            )
            notes.append(
                f"Partial ancestry coverage: no pinned {gene} frequencies for "
                f"{dropped_desc}. Those weights were renormalised away, so this "
                f"distribution describes only the covered "
                f"{', '.join(sorted(coverage.covered))} fraction of the cohort."
            )
            warnings.append(
                f"{gene} × {drug}: {coverage.dropped_weight:.0%} of declared "
                f"enrolment ({dropped_desc}) has no pinned frequency data and was "
                "excluded from the distribution."
            )

        findings.append(
            GeneDrugFinding(
                gene=gene,
                drug=drug,
                verdict=verdict,
                tier=Tier.DISTRIBUTION,
                distribution=dist,
                cpic_level=cpic_level,
                missing_exclusion=missing_exclusion,
                citations=citations,
                notes=notes,
                coverage=coverage,
            )
        )

        site_findings.extend(
            site_metabolic_burden(gene, per_pop_freqs, protocol.sites)
        )

    # Preserve order, drop duplicates.
    data_sources = list(dict.fromkeys(data_sources))

    return AuditReport(
        protocol_title=protocol.title,
        trial_id=protocol.trial_id,
        total_planned_n=protocol.total_planned_n,
        findings=findings,
        site_findings=site_findings,
        data_sources=data_sources,
        offline=offline,
        warnings=list(dict.fromkeys(warnings)),
    )
