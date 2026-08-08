"""The one hardcoded finding: DPYD screening vs fluoropyrimidine dosing.

CPIC guidance is unambiguous — genotype or phenotype DPYD before dosing a
fluoropyrimidine. This is a lookup against that one guideline, not a rule
engine: it exists for DPYD + fluoropyrimidines only, and should stay that way
until a second gene-drug pair earns its own rule.
"""

from __future__ import annotations

FLUOROPYRIMIDINES = frozenset({"capecitabine", "fluorouracil", "5-fu", "5-fluorouracil", "tegafur"})

_DPYD_SCREENING_TERMS = ("dpyd", "dpd deficiency", "dpd testing", "dihydropyrimidine")


def dpyd_screening_required(drugs: list[str]) -> bool:
    return any(drug.strip().lower() in FLUOROPYRIMIDINES for drug in drugs)


def dpyd_screening_present(criteria: list[str]) -> bool:
    text = " ".join(criteria).lower()
    return any(term in text for term in _DPYD_SCREENING_TERMS)
