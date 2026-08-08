"""Wires the Tier 0 engine, the pgx-core phenotype lookup, and the DPYD
screening-gap rule into one `AuditReport`.

Scope: DPYD x fluoropyrimidines only. Generalising to other genes/drugs is
future work, not a Tier 0-demo requirement.
"""

from __future__ import annotations

from . import rules
from .allele_frequencies import per_population_table
from .cohort import blend_allele_frequencies, cohort_ancestry_mix, diplotype_frequencies, phenotype_distribution
from .models import AuditReport, GeneDrugFinding, Protocol, Tier, Verdict
from .phenotype import phenotype_map

GENE = "DPYD"
CITATIONS = ["CPIC Guideline for Fluoropyrimidines and DPYD (Amstutz et al. 2018, updated 2024)"]
DATA_SOURCES = [
    "gnomAD v2.1.1 exomes (pinned allele frequencies)",
    "CPIC DPYD diplotype-phenotype table via anukriti-pgx-core",
]


def audit_protocol(protocol: Protocol) -> AuditReport:
    fluoropyrimidines = [d.drug for d in protocol.drugs if d.drug.strip().lower() in rules.FLUOROPYRIMIDINES]

    findings: list[GeneDrugFinding] = []
    if fluoropyrimidines:
        findings.append(_dpyd_finding(protocol, fluoropyrimidines[0]))

    return AuditReport(
        protocol_title=protocol.title,
        trial_id=protocol.trial_id,
        total_planned_n=protocol.total_planned_n,
        findings=findings,
        data_sources=DATA_SOURCES,
        offline=True,
    )


def _dpyd_finding(protocol: Protocol, drug: str) -> GeneDrugFinding:
    ancestry_mix = cohort_ancestry_mix(protocol.sites)
    blended = blend_allele_frequencies(per_population_table(GENE), ancestry_mix)
    diplotype_freqs = diplotype_frequencies(blended)
    pheno_of = phenotype_map(GENE, list(diplotype_freqs))
    distribution = phenotype_distribution(diplotype_freqs, pheno_of, protocol.total_planned_n)

    screened = rules.dpyd_screening_present(protocol.inclusion_criteria + protocol.exclusion_criteria)
    verdict = Verdict.NO_SIGNAL if screened else Verdict.ACTIONABLE

    return GeneDrugFinding(
        gene=GENE,
        drug=drug,
        verdict=verdict,
        tier=Tier.DISTRIBUTION,
        distribution=distribution,
        cpic_level="A",
        missing_exclusion=None if screened else "DPYD genotype/phenotype screening prior to dosing",
        citations=CITATIONS,
    )
