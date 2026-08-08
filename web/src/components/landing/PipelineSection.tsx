import { useState } from "react";
import { MetabolismStrip } from "./Characters";
import { Reveal } from "./Reveal";

const STEPS = [
  {
    num: "01 / Extract",
    title: "Protocol → structured claims",
    body: "Claude reads PDF, registry text, or JSON and fills the Protocol schema — drugs, dose, sites, planned N. Never a frequency.",
  },
  {
    num: "02 / Compute",
    title: "Ancestry-weighted arithmetic",
    body: "Hardy–Weinberg expansion on pinned gnomAD allele frequencies, blended by site ancestry mix. Pure Python, no network.",
  },
  {
    num: "03 / Find",
    title: "CPIC rules + screening gaps",
    body: "Diplotype → phenotype via anukriti-pgx-core. DPYD × fluoropyrimidine screening gaps flagged when exclusion criteria omit deficiency testing.",
  },
  {
    num: "04 / Report",
    title: "Tier-labelled audit output",
    body: "ACTIONABLE findings, per-site burden deltas, partial-coverage warnings — every claim carries a tier badge and provenance hook.",
  },
];

export function PipelineSection() {
  const [active, setActive] = useState(0);

  return (
    <section className="landing-section" id="pipeline">
      <p className="landing-label">The closed loop</p>
      <h2>
        Extraction stops at structure.
        <br />
        <span className="landing-accent">The engine decides the numbers.</span>
      </h2>
      <p className="landing-section-intro">
        Protocol prose never becomes a frequency. The closed loop keeps Claude on the extraction
        side and deterministic code on the verdict side — mirroring cohortfit&apos;s hard model
        boundary.
      </p>

      <MetabolismStrip />

      <Reveal className="landing-pipeline-card has-flow">
        <span className="pipeline-flow-dot" aria-hidden="true" />
        {STEPS.map((step, i) => (
          <button
            type="button"
            key={step.num}
            className={`landing-pipeline-step ${active === i ? "is-active" : ""}`}
            onMouseEnter={() => setActive(i)}
            onFocus={() => setActive(i)}
            onClick={() => setActive(i)}
            aria-pressed={active === i}
          >
            <span className="pipeline-step-index" aria-hidden="true">
              {String(i + 1).padStart(2, "0")}
            </span>
            <p className="landing-label">{step.num}</p>
            <h3>{step.title}</h3>
            <p>{step.body}</p>
          </button>
        ))}
      </Reveal>
    </section>
  );
}
