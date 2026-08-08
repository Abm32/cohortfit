import { useState } from "react";

const TABS = [
  { id: "sponsors", label: "Trial sponsors" },
  { id: "cros", label: "CROs" },
  { id: "sites", label: "Site selection" },
];

const CONTENT: Record<
  string,
  {
    title: string;
    items: { title: string; body: string }[];
    mock: {
      label: string;
      badge: string;
      badgeClass?: string;
      title: string;
      rows: string[];
      footer: string;
      trialId: string;
    };
  }
> = {
  sponsors: {
    title: "Know the PGx gap before first patient in.",
    items: [
      {
        title: "Reads what you already filed",
        body: "NCT01095003 prose, demo JSON, or pasted protocol — no new data entry layer.",
      },
      {
        title: "Surfaces missing DPYD screening",
        body: "CPIC Level A pairs flagged when exclusion criteria omit deficiency testing before fluoropyrimidine dosing.",
      },
      {
        title: "Expected phenotype distribution",
        body: "Tier 0 arithmetic on the cohort your sites will actually enrol — not the European reference the dose was written for.",
      },
      {
        title: "Offline demo ready",
        body: "Pinned fixtures and 128 pytest cases — run the audit without API keys or conference wifi.",
      },
    ],
    mock: {
      label: "AUDIT REPORT · TIER 0",
      badge: "ACTIONABLE",
      badgeClass: "landing-mock-badge-actionable",
      title: "DPYD × capecitabine — protocol does not exclude DPYD deficiency before dosing.",
      rows: [
        "Normal Metabolizer · 95.5% · 219.5 expected",
        "Intermediate Metabolizer · 4.5% · 10.4 expected",
        "Poor Metabolizer · 0.02% · 0.04 expected",
      ],
      footer: "Offline · pinned fixtures",
      trialId: "NCT01095003",
    },
  },
  cros: {
    title: "Operational feasibility, not just scientific.",
    items: [
      {
        title: "Site mix drives phenotype rate",
        body: "Same protocol, different ancestry blend — at-risk fraction shifts before a single patient enrols.",
      },
      {
        title: "Per-site burden ranking",
        body: "Munich ~6.4% at-risk vs Mumbai/Kochi ~3.55% — rate from ancestry, expected N from headcount.",
      },
      {
        title: "Partial coverage visible",
        body: "When pinned frequencies omit declared ancestries, coverage.dropped appears in warnings — not hidden in a sum-to-one table.",
      },
      {
        title: "Export-ready JSON",
        body: "AuditReport schema matches CLI output — same artifact for slides, filings, and the web viewer.",
      },
    ],
    mock: {
      label: "SITE BURDEN · DPYD",
      badge: "OFFLINE",
      title: "Munich 6.40% at-risk · 5.12 expected. Rate ratio 1.80× vs Mumbai.",
      rows: [
        "Mumbai — 3.55% · 3.55 expected · N=100",
        "Kochi — 3.55% · 1.77 expected · N=50",
        "Munich — 6.40% · 5.12 expected · N=80",
      ],
      footer: "Identical ancestry → same rate",
      trialId: "Demo protocol",
    },
  },
  sites: {
    title: "Pick sites with eyes open on metabolic mismatch.",
    items: [
      {
        title: "At-risk fraction per site",
        body: "Ancestry mix → allele blend → phenotype rate. Expected counts scale with planned enrolment.",
      },
      {
        title: "Rate ratio vs lowest site",
        body: "Munich runs ~1.8× the at-risk rate of Mumbai — robust across *2A sensitivity bounds.",
      },
      {
        title: "Headcount-only deltas labelled",
        body: "Mumbai and Kochi share SAS ancestry; UI distinguishes rate delta from N-only delta.",
      },
      {
        title: "No client-side math",
        body: "Landing page is static copy. Sort and display only in the audit app — fractions come from the engine.",
      },
    ],
    mock: {
      label: "COVERAGE · PARTIAL",
      badge: "WARNING",
      title: "No pinned DPYD frequencies for AFR, AMR (32% of enrolment). Distribution reflects EUR-covered fraction only.",
      rows: [
        "Covered: EUR 68%",
        "Dropped: AFR 13%, AMR 19%",
        "Logged in report.warnings[]",
      ],
      footer: "Population omission visible in JSON",
      trialId: "Partial coverage demo",
    },
  },
};

export function WhoItsForSection() {
  const [tab, setTab] = useState("sponsors");
  const content = CONTENT[tab];

  return (
    <section className="landing-section" id="audience">
      <p className="landing-label">Who it&apos;s for</p>
      <div className="landing-tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`landing-tab ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="landing-audience">
        <div>
          <h2>{content.title}</h2>
          <ul className="landing-audience-list" key={tab}>
            {content.items.map((item, i) => (
              <li
                key={item.title}
                className="audience-item-anim"
                style={{ "--reveal-delay": `${i * 70}ms` } as React.CSSProperties}
              >
                <span className="landing-audience-num">{i + 1}</span>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.body}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className="landing-mock-card mock-live" key={tab}>
          <div className="landing-mock-header">
            <span>COHORTFIT · DEMO</span>
            <span className={content.mock.badgeClass ?? "landing-mock-badge"}>
              {content.mock.badge}
            </span>
          </div>
          <div className="landing-mock-inner">
            <h4>{content.mock.label}</h4>
            <p className="landing-mock-title">{content.mock.title}</p>
            {content.mock.rows.map((row) => (
              <p key={row} className="landing-mock-row-text">
                {row}
              </p>
            ))}
          </div>
          <div className="landing-mock-footer">
            <span>{content.mock.footer}</span>
            <span>{content.mock.trialId}</span>
          </div>
        </div>
      </div>
    </section>
  );
}
