import { useEffect, useState } from "react";

export const AUDIT_STEPS = [
  "Validating Protocol schema",
  "Loading pinned gnomAD allele frequencies",
  "Blending site ancestry mix",
  "Hardy–Weinberg diplotype expansion",
  "Mapping CPIC phenotypes",
  "Applying screening-gap rules",
  "Assembling tier-labelled report",
] as const;

export const LOAD_REPORT_STEPS = [
  "Loading pinned AuditReport fixture",
  "Hydrating findings and site burden",
] as const;

interface Props {
  title: string;
  steps: readonly string[];
}

export function AuditProgressOverlay({ title, steps }: Props) {
  const [active, setActive] = useState(0);

  useEffect(() => {
    setActive(0);
    const id = window.setInterval(() => {
      setActive((i) => (i < steps.length - 1 ? i + 1 : i));
    }, 520);
    return () => window.clearInterval(id);
  }, [steps]);

  const progress = ((active + 1) / steps.length) * 100;

  return (
    <div className="audit-progress-overlay" role="dialog" aria-modal="true" aria-labelledby="audit-progress-title">
      <div className="audit-progress-card">
        <p className="landing-label" id="audit-progress-title">
          Running offline audit
        </p>
        <h2 className="audit-progress-heading">{title}</h2>
        <p className="audit-progress-sub">
          Deterministic engine — no LLM past extraction. Every Tier 0 number is arithmetic on
          pinned tables.
        </p>

        <div className="audit-progress-bar" aria-hidden="true">
          <div className="audit-progress-bar-fill" style={{ width: `${progress}%` }} />
        </div>

        <ol className="audit-progress-steps">
          {steps.map((step, i) => {
            const state = i < active ? "done" : i === active ? "active" : "pending";
            return (
              <li key={step} className={`audit-progress-step is-${state}`}>
                <span className="audit-progress-dot" aria-hidden="true" />
                <span>{step}</span>
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
