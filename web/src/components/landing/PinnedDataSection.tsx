const COLUMNS = [
  {
    label: "Pinned fixtures",
    title: "gnomAD v2.1.1, offline",
    body: "Allele frequencies ship as versioned JSON fixtures. Demo audits run without venue wifi — same inputs, same outputs, every time.",
  },
  {
    label: "CPIC tables",
    title: "13 genes via pgx-core",
    body: "Diplotype → phenotype lookups read canonical CPIC JSON from anukriti-pgx-core. No runtime PhenotypeEngine, no model-generated phenotypes.",
  },
  {
    label: "Tier discipline",
    title: "0 / 1 / Scenario",
    body: "Tier 0 is arithmetic only. Tier 1 needs a cited multiplier. Tier 2 is labelled scenario — never rendered like a prediction.",
  },
];

export function PinnedDataSection() {
  return (
    <section className="landing-section-dark" id="method">
      <div className="landing-section-inner">
        <p className="landing-label">Reproducibility</p>
        <h2>
          Every number is pinned
          <br />
          and reproducible.
        </h2>
        <p style={{ maxWidth: "640px" }}>
          If a reviewer cannot rerun the arithmetic from pinned inputs, the claim does not ship.
          cohortfit treats fixtures, CPIC tables, and tier labels as first-class contract — not
          footnotes.
        </p>
        <div className="landing-pinned-grid">
          {COLUMNS.map((col) => (
            <div key={col.label} className="landing-pinned-col">
              <p className="landing-label">{col.label}</p>
              <h3>{col.title}</h3>
              <p>{col.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
