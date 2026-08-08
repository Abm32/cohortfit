import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchSampleReport } from "./api/client";
import { AuditReportView } from "./components/AuditReportView";
import { DatasetCards } from "./components/DatasetCards";
import { FixtureLanding } from "./components/FixtureLanding";
import { ProtocolJsonInput } from "./components/ProtocolJsonInput";
import { ProtocolProseInput } from "./components/ProtocolProseInput";
import type { AuditReport } from "./types/audit";

type InputMode = "demo" | "json" | "prose";

const TABS: { id: InputMode; label: string }[] = [
  { id: "demo", label: "Demo" },
  { id: "json", label: "Paste Protocol JSON" },
  { id: "prose", label: "Extract from prose" },
];

function AuditApp() {
  const [report, setReport] = useState<AuditReport | null>(null);
  const [mode, setMode] = useState<InputMode>("demo");
  const [bootError, setBootError] = useState<string | null>(null);
  const [booting, setBooting] = useState(true);

  const receiveReport = useCallback((next: AuditReport) => {
    setReport(next);
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const sample = await fetchSampleReport();
        if (!cancelled) setReport(sample);
      } catch (e) {
        if (!cancelled) {
          setBootError(e instanceof Error ? e.message : "Failed to reach the audit API");
        }
      } finally {
        if (!cancelled) setBooting(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="app-header-brand">
          <span className="app-logo-mark">cf</span>
          cohortfit
        </Link>
        <h1>Audit workbench</h1>
        <span className="app-header-hint">Deterministic engine · same schema as the CLI</span>
      </header>

      <main className="app-main">
        <section className="app-controls">
          <div className="app-tabs" role="tablist" aria-label="Audit input mode">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={mode === tab.id}
                className={`app-tab ${mode === tab.id ? "is-active" : ""}`}
                onClick={() => setMode(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <div className="app-tabpanel">
            {mode === "demo" && (
              <>
                <DatasetCards onReport={receiveReport} />
                <FixtureLanding onReport={receiveReport} />
              </>
            )}
            {mode === "json" && <ProtocolJsonInput onReport={receiveReport} />}
            {mode === "prose" && <ProtocolProseInput onReport={receiveReport} />}
          </div>
        </section>

        {booting && <p className="app-loading">Loading pinned sample report…</p>}
        {bootError && !report && (
          <div className="app-error">
            <p>{bootError}</p>
            <p className="app-notes">
              Start the API and UI together: <code>cohortfit serve --port 8600</code>, then open{" "}
              <code>http://127.0.0.1:8600/app</code>.
            </p>
          </div>
        )}

        {report && (
          <div className="app-report" key={`${report.protocol_title}-${report.total_planned_n}`}>
            <AuditReportView report={report} />
          </div>
        )}
      </main>
    </div>
  );
}

export default AuditApp;
