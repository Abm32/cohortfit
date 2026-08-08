import { Link } from "react-router-dom";
import "../../landing.css";

export function HeroSection() {
  return (
    <section className="landing-hero" id="hero">
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
    </section>
  );
}
