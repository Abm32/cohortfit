import { useInView } from "../../hooks/useInView";
import { useCountUp } from "../../hooks/useCountUp";

interface Stat {
  value: string;
  label: string;
  /** Numeric target when the value should count up. */
  count?: number;
}

const STATS: Stat[] = [
  { value: "189", count: 189, label: "pytest cases passing — arithmetic pinned, regressions caught" },
  { value: "13", count: 13, label: "genes in pgx-core — canonical CPIC diplotype tables" },
  { value: "Tier 0", label: "arithmetic only — no LLM past Protocol extraction" },
  { value: "Offline", label: "by default — pinned fixtures, no venue wifi required" },
];

function StatValue({ stat, active }: { stat: Stat; active: boolean }) {
  const counted = useCountUp(stat.count ?? 0, active && stat.count !== undefined);
  if (stat.count === undefined) {
    return <div className="landing-stat">{stat.value}</div>;
  }
  return <div className="landing-stat">{Math.round(counted)}</div>;
}

export function ResultsSection() {
  const [ref, inView] = useInView<HTMLDivElement>({ threshold: 0.4 });

  return (
    <section className="landing-section" id="results">
      <p className="landing-label">Shipped today</p>
      <h2>
        Real numbers, <span className="landing-accent">already pinned.</span>
      </h2>
      <div className={`landing-results-grid ${inView ? "is-visible" : ""}`} ref={ref}>
        {STATS.map((stat, i) => (
          <div key={stat.value} className="landing-stat-cell" style={{ "--reveal-delay": `${i * 90}ms` } as React.CSSProperties}>
            <StatValue stat={stat} active={inView} />
            <div className="landing-stat-label">{stat.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
