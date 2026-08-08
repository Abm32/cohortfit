import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import {
  AUDIT_STEPS,
  AuditProgressOverlay,
  LOAD_REPORT_STEPS,
} from "./components/AuditProgressOverlay";
import { AuditReportView } from "./components/AuditReportView";
import { DatasetCards } from "./components/DatasetCards";
import { FixtureLanding } from "./components/FixtureLanding";
import { ProtocolJsonInput } from "./components/ProtocolJsonInput";
import { ProtocolProseInput } from "./components/ProtocolProseInput";
import type { AuditReport } from "./types/audit";

type InputMode = "demo" | "json" | "prose";
type AppPhase = "workbench" | "running" | "report";

const TABS: { id: InputMode; label: string }[] = [
  { id: "demo", label: "Demo" },
  { id: "json", label: "Paste Protocol JSON" },
  { id: "prose", label: "Extract from prose" },
];

const MIN_RUN_MS = 2200;

function AuditApp() {
  const [report, setReport] = useState<AuditReport | null>(null);
  const [mode, setMode] = useState<InputMode>("demo");
  const [phase, setPhase] = useState<AppPhase>("workbench");
  const [runTitle, setRunTitle] = useState("");
  const [runSteps, setRunSteps] = useState<readonly string[]>(AUDIT_STEPS);
  const [runError, setRunError] = useState<string | null>(null);

  const runAudit = useCallback(
    async (title: string, task: () => Promise<AuditReport>, steps: readonly string[] = AUDIT_STEPS) => {
      setRunError(null);
      setRunTitle(title);
      setRunSteps(steps);
      setPhase("running");

      const minDelay = new Promise<void>((resolve) => {
        window.setTimeout(resolve, MIN_RUN_MS);
      });

      try {
        const [result] = await Promise.all([task(), minDelay]);
        setReport(result);
        setPhase("report");
        window.scrollTo({ top: 0, behavior: "smooth" });
      } catch (e) {
        setPhase("workbench");
        setRunError(e instanceof Error ? e.message : "Audit failed");
      }
    },
    [],
  );

  const backToWorkbench = useCallback(() => {
    setPhase("workbench");
    setReport(null);
    setRunError(null);
  }, []);

  if (phase === "report" && report) {
    return (
      <div className="app-shell app-shell--report">
        <header className="app-result-header">
          <button type="button" className="app-btn app-btn-secondary" onClick={backToWorkbench}>
            ← New audit
          </button>
          <div className="app-result-header-meta">
            <span className="landing-label">Audit complete</span>
            <strong>{report.protocol_title}</strong>
          </div>
          <Link to="/" className="app-header-brand">
            cohortfit
          </Link>
        </header>
        <main className="app-main app-main--report">
          <AuditReportView report={report} />
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      {phase === "running" && <AuditProgressOverlay title={runTitle} steps={runSteps} />}

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
                disabled={phase === "running"}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <div className="app-tabpanel">
            {mode === "demo" && (
              <>
                <DatasetCards onRunAudit={runAudit} disabled={phase === "running"} />
                <FixtureLanding onRunAudit={runAudit} disabled={phase === "running"} />
              </>
            )}
            {mode === "json" && (
              <ProtocolJsonInput onRunAudit={runAudit} disabled={phase === "running"} />
            )}
            {mode === "prose" && (
              <ProtocolProseInput onRunAudit={runAudit} disabled={phase === "running"} />
            )}
          </div>
        </section>

        {runError && (
          <div className="empty-state panel app-report">
            <p className="error-box">{runError}</p>
          </div>
        )}

        {phase === "workbench" && !runError && (
          <div className="empty-state panel app-report">
            <p>No audit loaded yet</p>
            <p className="footnote">
              Pick a protocol card and click Run audit, use the Demo buttons, paste Protocol JSON,
              or extract from prose. Results open full-screen when the engine finishes.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default AuditApp;
