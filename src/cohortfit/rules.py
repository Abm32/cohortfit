"""CPIC screening-gap rules — hardcoded for demo scope.

One gene-drug pair per rule. Generalisation is roadmap, not hour-two scope.
"""

from __future__ import annotations

from anukriti_pgx_core.phenotype.recommendation_level import details_for, level_for

from .models import Protocol, Verdict

# Normalised drug name → gene symbol (fluoropyrimidine / DPYD demo path only).
_DRUG_TO_GENE: dict[str, str] = {
    "capecitabine": "DPYD",
    "fluorouracil": "DPYD",
    "5-fu": "DPYD",
    "5_fluorouracil": "DPYD",
    "5-fluorouracil": "DPYD",
}

# Terms that indicate the protocol already addresses PGx screening.
# String matching is intentional for pinned demo protocols — not a general NLP claim.
_SCREENING_TERMS = (
    "dpyd",
    "dpd",
    "dihydropyrimidine dehydrogenase",
    "dihydropyrimidine",
    "genotype",
    "genetic testing",
    "pharmacogen",
    "pharmacogenomic",
)

_DEFAULT_DPYD_PMID = "29152729"


def normalize_drug(drug: str) -> str:
    """Lowercase, strip, unify hyphens/underscores for lookup."""
    return drug.strip().lower().replace("_", "-")


def resolve_gene(drug: str) -> str | None:
    """Map a protocol drug name to a PGx gene symbol, or None if unsupported."""
    return _DRUG_TO_GENE.get(normalize_drug(drug))


def _criteria_text(protocol: Protocol) -> str:
    lines = protocol.inclusion_criteria + protocol.exclusion_criteria
    return "\n".join(lines).lower()


def mentions_screening(protocol: Protocol, gene: str) -> bool:
    """True if inclusion/exclusion criteria reference PGx screening for this gene."""
    text = _criteria_text(protocol)
    gene_lower = gene.lower()
    if gene_lower in text:
        return True
    return any(term in text for term in _SCREENING_TERMS)


def screening_gap(
    protocol: Protocol,
    drug: str,
    gene: str,
) -> tuple[Verdict, str | None, list[str]]:
    """Check whether a CPIC Level A pair lacks genotype screening in the protocol.

    Returns:
        (verdict, missing_exclusion message or None, citation PMIDs)
    """
    if resolve_gene(drug) != gene:
        return Verdict.NO_SIGNAL, None, []

    cpic_level = level_for(gene, normalize_drug(drug))
    if cpic_level != "A":
        return Verdict.NO_SIGNAL, None, []

    if mentions_screening(protocol, gene):
        return Verdict.NO_SIGNAL, None, []

    detail = details_for(gene, normalize_drug(drug))
    citations = list(detail.get("citations") or [])
    if not citations:
        citations = [_DEFAULT_DPYD_PMID]

    drug_display = drug.strip()
    message = (
        f"Protocol does not exclude or screen for {gene} deficiency before "
        f"{drug_display} dosing (CPIC Level A; test before fluoropyrimidines)."
    )
    return Verdict.ACTIONABLE, message, citations
