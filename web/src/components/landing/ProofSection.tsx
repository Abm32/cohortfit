import { useInView } from "../../hooks/useInView";

const SITES = [
  { name: "Mumbai", rate: "3.55%", height: 55 },
  { name: "Kochi", rate: "3.55%", height: 55 },
  { name: "Munich", rate: "6.40%", height: 100, highlight: true },
];

export function ProofSection() {
  const [chartRef, inView] = useInView<HTMLDivElement>({ threshold: 0.35 });

  return (
    <section className="landing-section-dark" id="findings">
      <div className="landing-section-inner landing-proof-grid">
        <div>
          <p className="landing-label">Site burden</p>
          <h2>Proof your IRB can read.</h2>
          <p>
            Every Tier 0 number traces to pinned gnomAD fixtures and CPIC diplotype tables. Site
            ranking &quot;Munich above Mumbai&quot; holds across the full *2A sensitivity range —
            ancestry drives rate, enrolment drives count.
          </p>
          <p>
            Leave-one-out ablation on HapB3 shows 94.2% of South Asian actionable burden on a
            single allele — derived from the fixture, not model-generated.
          </p>
        </div>
        <div className="landing-chart-card" ref={chartRef}>
          <div className="landing-chart-header">
            <span>AT-RISK RATE BY SITE · DPYD</span>
            <span className="landing-chart-stat">
              Munich 1.80×
              <br />
              vs Mumbai
            </span>
          </div>
          <p className="landing-chart-title">Ancestry drives rate. Enrolment drives count.</p>
          <div
            className={`landing-bar-chart ${inView ? "is-visible" : ""}`}
            role="img"
            aria-label="DPYD at-risk rate by site: Mumbai 3.55%, Kochi 3.55%, Munich 6.40%"
          >
            {SITES.map((site, i) => (
              <div key={site.name} className="landing-bar">
                <span className="landing-bar-value">{site.rate}</span>
                <div
                  className={`landing-bar-fill${site.highlight ? " highlight" : ""}`}
                  style={
                    {
                      "--bar-h": `${site.height}%`,
                      "--bar-delay": `${i * 140}ms`,
                    } as React.CSSProperties
                  }
                  aria-hidden="true"
                />
                <span className="landing-bar-label">{site.name}</span>
              </div>
            ))}
          </div>
          <div className="landing-chart-legend">
            <span>Mumbai · Kochi · Munich</span>
            <span>— Pinned fixture audit</span>
          </div>
        </div>
      </div>
    </section>
  );
}
