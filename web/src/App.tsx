import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
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

  const receiveReport = useCallback((next: AuditReport) => {
    setReport(next);
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
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

        {report ? (
          <div className="app-report" key={`${report.protocol_title}-${report.total_planned_n}`}>
            <AuditReportView report={report} />
          </div>
        ) : (
          <div className="empty-state panel app-report">
            <p>No audit loaded yet</p>
            <p className="footnote">
              Use the Demo tab to load the sample report or run a demo audit, pick a pinned
              protocol card, paste Protocol JSON, or extract from prose.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default AuditApp;
