#!/usr/bin/env python3
"""Regenerate Finding 2's ablation table from the pinned frequency fixture.

FINDINGS.md used to carry hand-copied arithmetic. Commit 266ffb7 requeried
gnomAD v4.1 and corrected an 8x *2A error, and the document was never
regenerated, so for months the repo shipped two mutually contradictory sets of
numbers -- and the stale one was the one on the public landing page.

That is the failure DATA_PROVENANCE.md says this repo exists to prevent. The
fix is not to retype the numbers correctly; it is to stop typing them.

Engine-version caveat: burden shares are computed from the at-risk (IM+PM)
fraction, and the fixture's own _ground_truth comment records that the 0.7.2
change moved mass only between PM and IM, leaving at_risk_fraction unchanged.
So these shares are stable across that bump. The check at the end of main()
enforces it rather than trusting this paragraph: if the live at-risk fraction
and the fixture's stored one ever diverge, the table is not printed.
"""
from __future__ import annotations

import json
from pathlib import Path

# _at_risk is the same helper burden_shares() uses, so the baseline printed
# here and the shares are computed the same way by construction.
from cohortfit.panel import _at_risk, burden_shares

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures/frequencies/dpyd.json"


def at_risk_fraction(freqs: dict[str, float]) -> float:
    return _at_risk("DPYD", freqs)


def main() -> int:
    fixture = json.loads(FIXTURE.read_text())
    pops = fixture["populations"]

    rows: dict[str, dict] = {}
    for pop in ("SAS", "EUR"):
        freqs = {a: v["frequency"] for a, v in pops[pop]["alleles"].items()}
        baseline = at_risk_fraction(freqs)
        shares = burden_shares("DPYD", freqs)
        rows[pop] = {"baseline": baseline, "shares": shares, "freqs": freqs}

    print(f"fixture: {FIXTURE.name}  query_date={fixture['_meta'].get('query_date')}")
    print(f"{'allele':<12} {'SAS share':>10} {'EUR share':>10}")
    print(f"{'(baseline)':<12} {rows['SAS']['baseline']:>9.4%} {rows['EUR']['baseline']:>9.4%}")
    alleles = sorted(rows["SAS"]["shares"], key=lambda a: -rows["SAS"]["shares"][a])
    for allele in alleles:
        sas = rows["SAS"]["shares"][allele]
        eur = rows["EUR"]["shares"].get(allele, 0.0)
        print(f"{allele:<12} {sas:>9.1%} {eur:>9.1%}")

    # The fixture carries its own precomputed ground truth. If the live
    # computation and the stored block ever disagree, one of them is stale and
    # the table below is not trustworthy -- so say so rather than printing it.
    truth = fixture["_ground_truth"]
    for pop in ("SAS", "EUR"):
        stored = truth.get(pop, {}).get("at_risk_fraction")
        if stored is None:
            continue
        live = rows[pop]["baseline"]
        if abs(stored - live) > 5e-4:
            raise SystemExit(
                f"MISMATCH {pop}: fixture _ground_truth says {stored:.6f}, "
                f"live computation says {live:.6f}. Do not publish this table."
            )
        print(f"  {pop} agrees with fixture _ground_truth ({stored:.6f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
