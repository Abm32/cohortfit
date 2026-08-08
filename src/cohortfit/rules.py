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

# Terms that name *this gene's* deficiency directly. Any of these is sufficient
# evidence the protocol addresses DPYD screening.
_DPYD_SPECIFIC_TERMS = (
    "dpyd",
    "dpd",
    "dihydropyrimidine dehydrogenase",
    "dihydropyrimidine",
)

# Generic PGx vocabulary. NOT sufficient on its own: an oncology protocol that
# excludes on HER2, KRAS or EGFR genotype says nothing about DPYD, and treating
# it as screened is a false negative on exactly the finding this tool exists to
# produce. These only count when they co-occur with a gene-specific term inside
# the *same* criterion.
_GENERIC_PGX_TERMS = (
    "genotype",
    "genetic testing",
    "pharmacogen",
    "pharmacogenomic",
)

_DEFAULT_DPYD_PMID = "29152729"

# Gene symbol -> terms naming that gene's deficiency.
_GENE_SPECIFIC_TERMS: dict[str, tuple[str, ...]] = {
    "DPYD": _DPYD_SPECIFIC_TERMS,
}


def normalize_drug(drug: str) -> str:
    """Lowercase, strip, unify hyphens/underscores for lookup."""
    return drug.strip().lower().replace("_", "-")


def resolve_gene(drug: str) -> str | None:
    """Map a protocol drug name to a PGx gene symbol, or None if unsupported."""
    return _DRUG_TO_GENE.get(normalize_drug(drug))


def _criteria_lines(protocol: Protocol) -> list[str]:
    return [
        line.lower()
        for line in protocol.inclusion_criteria + protocol.exclusion_criteria
    ]


def mentions_screening(protocol: Protocol, gene: str) -> bool:
    """True if inclusion/exclusion criteria reference PGx screening for *this gene*.

    Matching is deliberately gene-scoped. A criterion must either name the gene
    or its enzyme deficiency directly, or pair generic pharmacogenomic wording
    with a gene-specific term in the same criterion. Matching generic terms
    alone across the whole criteria block would mark any protocol that
    genotypes an unrelated marker (HER2, KRAS, EGFR) as DPYD-screened — a
    false NO_SIGNAL on the finding this tool exists to produce.

    String matching remains intentional for pinned demo protocols; it is not a
    general NLP claim.
    """
    gene_lower = gene.lower()
    specific_terms = _GENE_SPECIFIC_TERMS.get(gene, (gene_lower,))

    for line in _criteria_lines(protocol):
        if gene_lower in line:
            return True
        if any(term in line for term in specific_terms):
            return True
        if any(term in line for term in _GENERIC_PGX_TERMS) and any(
            term in line for term in specific_terms
        ):
            return True
    return False


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


# Allele -> (pmid, one-line description of the dispute). Sourced from
# EVIDENCE.md section 5: CPIC's own fluoropyrimidine/DPYD guideline page flags
# Knikman et al., J Clin Oncol 2023 (PMID 37639651). The dispute is inside CPIC,
# not between outside cohorts, which is what makes it a verdict rather than a
# caveat.
_CONTESTED_ALLELES: dict[str, dict[str, tuple[str, str]]] = {
    "DPYD": {
        "HapB3": (
            "37639651",
            (
                "CPIC reports evidence of reduced treatment effectiveness and "
                "significantly increased toxicity in HapB3 carriers dosed at "
                "the standard 25% reduction"
            ),
        ),
    },
}

# Share of the cohort's at-risk burden at which a contested allele decides the
# verdict. A judgement call, not a derived constant: it marks where the disputed
# dose action covers most screen-positives instead of a minority of them.
# EUR (0.639, FINDINGS.md Finding 2) clears it as well as SAS (0.942). That is
# intended — the verdict tracks the dosing dispute, not the population.
_CONTESTED_BURDEN_THRESHOLD = 0.60


def contested_burden(
    gene: str,
    drug: str,
    burden_shares: dict[str, float],
) -> tuple[str, str, list[str]] | None:
    """Flag when a contested-dosing allele dominates this cohort's actionable burden.

    Returns (allele, message, citations) or None when no contested allele
    clears the threshold. The caller builds the GeneDrugFinding — this stays a
    pure function over an already-computed burden share map so it is testable
    without loading a fixture.
    """
    contested = _CONTESTED_ALLELES.get(gene)
    if not contested:
        return None

    over_threshold = [
        (share, allele)
        for allele, share in burden_shares.items()
        if allele in contested and share >= _CONTESTED_BURDEN_THRESHOLD
    ]
    if not over_threshold:
        return None

    share, allele = max(over_threshold)
    pmid, dispute = contested[allele]
    message = (
        f"{allele} carries {share:.1%} of this cohort's actionable {gene} "
        f"burden, and CPIC's recommended dose action for {allele} is disputed: "
        f"{dispute} (PMID {pmid}). For most {drug.strip()} screen-positives in "
        f"this cohort there is no settled clinical response."
    )
    return allele, message, [pmid]
