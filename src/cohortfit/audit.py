"""Audit orchestrator — the only module that knows the full Tier 0 pipeline.

Claude fills ``Protocol``; everything in this module is deterministic arithmetic
on pinned fixtures and pgx-core tables. No LLM, no network when ``offline=True``.
"""

from __future__ import annotations

import json
from pathlib import Path

from anukriti_pgx_core.phenotype.recommendation_level import level_for

from .cohort import blend_allele_frequencies, cohort_ancestry_mix
from .frequencies import FixtureError, load_gene_frequencies, load_gene_provenance
from .models import AuditReport, GeneDrugFinding, Protocol, SiteFinding, Tier
from .pgx import cohort_phenotype_distribution, table_citation
from .rules import normalize_drug, resolve_gene, screening_gap

_AT_RISK_PHENOTYPES = frozenset({"Poor Metabolizer", "Intermediate Metabolizer"})


def load_protocol(path: Path | str) -> Protocol:
    """Load and validate a protocol JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Protocol.model_validate(data)


def _at_risk_fraction(distribution) -> float:
    return sum(d.fraction for d in distribution if d.phenotype in _AT_RISK_PHENOTYPES)


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

    data_sources: list[str] = []
    findings: list[GeneDrugFinding] = []
    site_findings: list[SiteFinding] = []

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
        data_sources.append(
            f"gnomAD {gnomad_version} allele frequencies for {gene} "
            f"(query_date={query_date}, fixture=frequencies/{gene.lower()}.json)"
        )

        # Cohort-wide distribution (enrolment-weighted ancestry mix).
        mix = cohort_ancestry_mix(protocol.sites)
        blended = blend_allele_frequencies(per_pop_freqs, mix)
        if not blended:
            continue

        dist, table = cohort_phenotype_distribution(
            gene, blended, protocol.total_planned_n
        )
        data_sources.append(table_citation(table))

        verdict, missing_exclusion, citations = screening_gap(protocol, drug, gene)
        cpic_level = level_for(gene, normalize_drug(drug)) or None

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
            )
        )

        # Per-site metabolic burden (site-selection deltas).
        for site in protocol.sites:
            site_blended = blend_allele_frequencies(per_pop_freqs, site.ancestry_mix)
            if not site_blended:
                continue
            site_dist, _ = cohort_phenotype_distribution(
                gene, site_blended, site.planned_n
            )
            at_risk = _at_risk_fraction(site_dist)
            site_findings.append(
                SiteFinding(
                    site_name=site.name,
                    gene=gene,
                    at_risk_fraction=at_risk,
                    expected_at_risk_n=at_risk * site.planned_n,
                )
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
    )
