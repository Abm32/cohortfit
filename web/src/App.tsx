import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

interface PhenotypeCount {
  phenotype: string;
  fraction: number;
  expected_n: number;
}

interface Finding {
  gene: string;
  drug: string;
  verdict: string;
  tier: number;
  distribution: PhenotypeCount[];
  missing_exclusion: string | null;
  notes: string[];
}

interface SiteFinding {
  site_name: string;
  at_risk_fraction: number;
  expected_at_risk_n: number;
}

interface AuditReport {
  protocol_title: string;
  trial_id: string | null;
  total_planned_n: number;
  offline: boolean;
  warnings: string[];
  findings: Finding[];
  site_findings: SiteFinding[];
}

const API = import.meta.env.DEV ? "/api" : "";

function formatFraction(f: number): string {
  const pct = f * 100;
  if (pct === 0) return "0%";
  if (pct < 0.01) return `${pct.toFixed(3)}%`;
  if (pct < 1) return `${pct.toFixed(2)}%`;
  return `${pct.toFixed(1)}%`;
}

function formatN(n: number): string {
  if (n === 0) return "0";
  if (n < 0.1) return n.toFixed(2);
  return n.toFixed(1);
}

function tierLabel(t: number): string {
  if (t === 0) return "TIER 0";
  if (t === 1) return "TIER 1";
  return "SCENARIO";
}

function AuditApp() {
  const [report, setReport] = useState<AuditReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSample = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/fixtures/reports/sample`);
      if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
      setReport(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load report");
    } finally {
      setLoading(false);
    }
  }, []);

  const runDemoAudit = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const protoRes = await fetch(`${API}/fixtures/protocols/demo`);
      if (!protoRes.ok) throw new Error("Demo protocol unavailable — is cohortfit serve running?");
      const protocol = await protoRes.json();
      const auditRes = await fetch(`${API}/audit?offline=true`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(protocol),
      });
      if (!auditRes.ok) throw new Error(`${auditRes.status}: ${await auditRes.text()}`);
      setReport(await auditRes.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Audit failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSample();
  }, [loadSample]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="app-header-brand">
          <span className="app-logo-mark">cf</span>
          cohortfit
        </Link>
        <h1>Audit report</h1>
        <div className="app-header-actions">
          <button
            type="button"
            className="app-btn app-btn-secondary"
            disabled={loading}
            onClick={() => void loadSample()}
          >
            Sample
          </button>
          <button type="button" className="app-btn" disabled={loading} onClick={() => void runDemoAudit()}>
            Live audit
          </button>
        </div>
      </header>
      <main className="app-main">
        {loading && <p className="app-loading">Loading…</p>}
        {error && (
          <div className="app-error">
            <p>{error}</p>
            <p className="app-notes">
              Start the API: <code>cohortfit serve --port 8000</code>
            </p>
          </div>
        )}
        {report && (
          <>
            <div className="app-panel">
              <h2>{report.protocol_title}</h2>
              <p className="app-meta">
                {report.trial_id && `Trial ${report.trial_id} · `}
                N={report.total_planned_n} · {report.offline ? "offline" : "live"}
              </p>
            </div>
            {report.warnings.length > 0 && (
              <div className="app-warnings">
                <h2>Warnings</h2>
                <ul>
                  {report.warnings.map((w) => (
                    <li key={w.slice(0, 40)}>{w}</li>
                  ))}
                </ul>
              </div>
            )}
            {report.findings.map((f) => (
              <div key={`${f.gene}-${f.tier}`} className="app-panel">
                <p>
                  <span className={`app-tier-${f.tier}`}>{tierLabel(f.tier)}</span>
                  {" · "}
                  <strong>
                    {f.gene} × {f.drug}
                  </strong>
                  {" · "}
                  <span className={`app-verdict-${f.verdict.toLowerCase()}`}>{f.verdict}</span>
                </p>
                {f.missing_exclusion && <p>{f.missing_exclusion}</p>}
                {f.distribution.length > 0 && (
                  <table className="app-table">
                    <thead>
                      <tr>
                        <th>Phenotype</th>
                        <th>Fraction</th>
                        <th>Expected N</th>
                      </tr>
                    </thead>
                    <tbody>
                      {f.distribution.map((row) => (
                        <tr key={row.phenotype}>
                          <td>{row.phenotype}</td>
                          <td>{formatFraction(row.fraction)}</td>
                          <td>{formatN(row.expected_n)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
                {f.notes.map((n) => (
                  <p key={n.slice(0, 30)} className="app-notes">
                    {n}
                  </p>
                ))}
              </div>
            ))}
            {report.site_findings.length > 0 && (
              <div className="app-panel">
                <h3>Site burden</h3>
                <table className="app-table">
                  <thead>
                    <tr>
                      <th>Site</th>
                      <th>At-risk rate</th>
                      <th>Expected N</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...report.site_findings]
                      .sort((a, b) => b.at_risk_fraction - a.at_risk_fraction)
                      .map((s) => (
                        <tr key={s.site_name}>
                          <td>{s.site_name}</td>
                          <td>{formatFraction(s.at_risk_fraction)}</td>
                          <td>{formatN(s.expected_at_risk_n)}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default AuditApp;
