const STATS = [
  { value: "128", label: "pytest cases passing — arithmetic pinned, regressions caught" },
  { value: "13", label: "genes in pgx-core — canonical CPIC diplotype tables" },
  { value: "Tier 0", label: "arithmetic only — no LLM past Protocol extraction" },
  { value: "Offline", label: "by default — pinned fixtures, no venue wifi required" },
];

export function ResultsSection() {
  return (
    <section className="landing-section" id="results">
      <p className="landing-label">Shipped today</p>
      <h2>
        Real numbers,{" "}
        <span className="landing-accent">already pinned.</span>
      </h2>
      <div className="landing-results-grid">
        {STATS.map((stat) => (
          <div key={stat.value}>
            <div className="landing-stat">{stat.value}</div>
            <div className="landing-stat-label">{stat.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
