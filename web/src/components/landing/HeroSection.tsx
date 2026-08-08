import { lazy, Suspense, useState } from "react";
import { Link } from "react-router-dom";

// Code-split three.js: the landing paints immediately, the helix streams in.
const DnaHelix = lazy(() =>
  import("../../three/DnaHelix").then((m) => ({ default: m.DnaHelix })),
);

// Pinned Tier 0 at-risk (IM+PM) rates from the demo audit fixture.
const EUR_RATE = 6.4;
const SAS_RATE = 3.55;

export function HeroSection() {
  const [sasPct, setSasPct] = useState(70);
  const sas = sasPct / 100;
  const atRisk = EUR_RATE * (1 - sas) + SAS_RATE * sas;

  return (
    <section className="landing-hero landing-hero-grid" id="hero">
      <div className="landing-hero-copy">
        <p className="landing-label">PGx feasibility for clinical trials</p>
        <h1>
          Audit the cohort your protocol will{" "}
          <span className="landing-accent">actually</span> recruit.
        </h1>
        <p className="landing-hero-lead">
          Claude extracts structured claims from protocol prose — drugs, dose regimen, sites,
          inclusion criteria. The deterministic engine computes phenotype distributions, screening
          gaps, and per-site metabolic burden from pinned CPIC tables and gnomAD fixtures.
        </p>

        <div className="hero-mixer" role="group" aria-label="Ancestry mix simulator">
          <div className="hero-mixer-head">
            <span className="landing-label">Site ancestry mix</span>
            <span className="hero-mixer-readout">
              <strong>{atRisk.toFixed(2)}%</strong> expected at-risk (IM+PM)
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={100}
            value={sasPct}
            onChange={(e) => setSasPct(Number(e.target.value))}
            className="hero-mixer-slider"
            aria-label="South Asian ancestry percentage"
          />
          <div className="hero-mixer-scale">
            <span>{100 - sasPct}% EUR</span>
            <span>{sasPct}% SAS</span>
          </div>
          <p className="hero-mixer-note">
            Same protocol, same dose — drag the cohort and watch the DPYD panel light up. The number
            is real Tier 0 arithmetic; the helix is the population it lands on.
          </p>
        </div>

        <div className="landing-hero-actions">
          <Link to="/app" className="landing-btn landing-btn-primary">
            Run demo audit
          </Link>
          <Link to="/app" className="landing-btn landing-btn-secondary">
            See the sample report
          </Link>
        </div>
        <p className="landing-trust">
          No LLM past extraction. Every Tier 0 number is arithmetic you can rerun offline.
        </p>
      </div>

      <div className="landing-hero-visual">
        <div className="landing-hero-canvas">
          <Suspense fallback={<div className="landing-hero-canvas-fallback" />}>
            <DnaHelix mix={sas} />
          </Suspense>
        </div>
        <div className="landing-hero-legend">
          <span><i className="dot dot-forest" /> DPYD strand</span>
          <span><i className="dot dot-mint" /> base pair</span>
          <span><i className="dot dot-amber" /> actionable</span>
        </div>
      </div>
    </section>
  );
}
