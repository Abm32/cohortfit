#!/usr/bin/env python3
"""Regenerate every computable number in docs/FINDINGS.md from the fixture.

FINDINGS.md used to carry hand-copied arithmetic. Commit 266ffb7 requeried
gnomAD v4.1 and corrected an 8x *2A error, and the document was never
regenerated, so for months the repo shipped two mutually contradictory sets of
numbers -- and the stale one was the one on the public landing page.

That is the failure DATA_PROVENANCE.md says this repo exists to prevent. The
fix is not to retype the numbers correctly; it is to stop typing them.

Covers Findings 1, 2, 3, 5 and 6. Findings 4, 7 and 8 are not emitted here:
4 is retracted, and 7 and 8 rest on external literature and market data that
this fixture cannot produce.

Engine-version caveat: burden shares are computed from the at-risk (IM+PM)
fraction, and the fixture's own _ground_truth comment records that the 0.7.2
change moved mass only between PM and IM, leaving at_risk_fraction unchanged.
So these shares are stable across that bump. check_against_fixture() enforces
it rather than trusting this paragraph: if the live at-risk fraction and the
fixture's stored one ever diverge, the script exits non-zero.
"""
from __future__ import annotations

import json
from pathlib import Path

# _at_risk is the same helper burden_shares() uses, so the baselines printed
# here and the shares are computed the same way by construction.
from cohortfit.panel import _at_risk, burden_shares, panel_concentration
from cohortfit.pgx import cohort_phenotype_distribution

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures/frequencies/dpyd.json"
POPS = ("SAS", "EUR")
CONTESTED = "HapB3"


def freqs_for(fixture: dict, pop: str) -> dict[str, float]:
    return {a: v["frequency"] for a, v in fixture["populations"][pop]["alleles"].items()}


def blend(a: dict[str, float], b: dict[str, float], frac_b: float) -> dict[str, float]:
    """Mix two allele pools. Linear in allele space, which is the claim Finding 6 makes."""
    keys = set(a) | set(b)
    return {k: a.get(k, 0.0) * (1 - frac_b) + b.get(k, 0.0) * frac_b for k in keys}


def check_against_fixture(fixture: dict) -> None:
    truth = fixture["_ground_truth"]
    for pop in POPS:
        stored = truth.get(pop, {}).get("at_risk_fraction")
        if stored is None:
            continue
        live = _at_risk("DPYD", freqs_for(fixture, pop))
        if abs(stored - live) > 5e-4:
            raise SystemExit(
                f"MISMATCH {pop}: fixture _ground_truth says {stored:.6f}, live "
                f"computation says {live:.6f}. Do not publish these tables."
            )
        print(f"  {pop} agrees with fixture _ground_truth ({stored:.6f})")


def finding_1(fixture: dict) -> None:
    print("\n## Finding 1 — leave-one-out ablation + concentration\n")
    base = {p: _at_risk("DPYD", freqs_for(fixture, p)) for p in POPS}
    shares = {p: burden_shares("DPYD", freqs_for(fixture, p)) for p in POPS}
    print(f"| Allele removed | Share of SAS burden | Share of EUR burden |")
    print(f"|---|---:|---:|")
    print(f"| *(none — baseline at-risk)* | {base['SAS']:.4%} | {base['EUR']:.4%} |")
    for allele in sorted(shares["SAS"], key=lambda a: -shares["SAS"][a]):
        print(f"| `{allele}` | {shares['SAS'][allele]:.1%} | {shares['EUR'].get(allele, 0.0):.1%} |")

    print("\n| Population | Total variant load | HHI | Effective # alleles | Dominant |")
    print("|---|---:|---:|---:|---|")
    for p in POPS:
        c = panel_concentration(freqs_for(fixture, p))
        print(f"| {p} | {c.total_variant_load:.3%} | {c.hhi:.3f} | **{c.effective_alleles:.2f}** "
              f"| {c.dominant_allele} ({c.dominant_share:.1%}) |")


def finding_2(fixture: dict) -> None:
    """What is left if the contested allele's dose guidance is set aside."""
    print(f"\n## Finding 2 — ablating the contested allele ({CONTESTED})\n")
    print("| Population | Full at-risk | Retained on unambiguous alleles | Share retaining clear guidance | NNS |")
    print("|---|---:|---:|---:|---:|")
    for p in POPS:
        f = freqs_for(fixture, p)
        full = _at_risk("DPYD", f)
        ablated = {a: v for a, v in f.items() if a != CONTESTED}
        ablated["*1"] = ablated.get("*1", 0.0) + f.get(CONTESTED, 0.0)
        retained = _at_risk("DPYD", ablated)
        share = retained / full if full else 0.0
        nns = 1 / retained if retained else float("inf")
        print(f"| {p} | {full:.3%} | **{retained:.3%}** | **{share:.1%}** | {nns:.0f} |")


def finding_3(fixture: dict) -> None:
    print("\n## Finding 3 — number needed to screen\n")
    print("| Population | At-risk | NNS |")
    print("|---|---:|---:|")
    nns = {}
    for p in ("EUR", "SAS"):
        r = _at_risk("DPYD", freqs_for(fixture, p))
        nns[p] = 1 / r
        print(f"| {p} | {r:.3%} | **{nns[p]:.1f}** |")
    print(f"\nSAS needs **{nns['SAS'] / nns['EUR']:.2f}x** more tests per actionable finding.")


def finding_5(fixture: dict) -> None:
    print("\n## Finding 5 — expected Poor Metabolizers, 100% SAS cohort\n")
    f = freqs_for(fixture, "SAS")
    print("| Cohort n | Expected PM | Expected IM |")
    print("|---|---:|---:|")
    for n in (150, 230, 1000, 5000):
        counts, _ = cohort_phenotype_distribution("DPYD", f, n)
        by = {c.phenotype: c.expected_n for c in counts}
        print(f"| {n:,} | {by.get('Poor Metabolizer', 0):.3f} | {by.get('Intermediate Metabolizer', 0):.1f} |")
    pm_frac = next(
        (c.fraction for c in cohort_phenotype_distribution("DPYD", f, 1)[0]
         if c.phenotype == "Poor Metabolizer"), 0.0)
    if pm_frac:
        print(f"\nOne expected PM at n = **{1 / pm_frac:,.0f}**.")


def finding_6(fixture: dict) -> None:
    print("\n## Finding 6 — ancestry mix sweep\n")
    sas, eur = freqs_for(fixture, "SAS"), freqs_for(fixture, "EUR")
    print("| EUR fraction | At-risk |")
    print("|---:|---:|")
    pts = []
    for frac in (0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.0):
        r = _at_risk("DPYD", blend(sas, eur, frac))
        pts.append((frac, r))
        print(f"| {frac:.0%} | {r:.4%} |")
    lo, hi = pts[0][1], pts[-1][1]
    print(f"\nEach 10 percentage points of European enrolment adds "
          f"~**{(hi - lo) / 10:.3%}** of expected at-risk burden (linear fit end to end).")


def main() -> int:
    fixture = json.loads(FIXTURE.read_text())
    print(f"fixture: {FIXTURE.name}  query_date={fixture['_meta'].get('query_date')}")
    check_against_fixture(fixture)
    for fn in (finding_1, finding_2, finding_3, finding_5, finding_6):
        fn(fixture)
    print("\nFindings 4, 7, 8 are not generated here: 4 is retracted; 7 and 8 rest "
          "on external literature and market data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
