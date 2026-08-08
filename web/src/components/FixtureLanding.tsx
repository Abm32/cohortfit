import { useState } from "react";
import { auditProtocol, fetchDemoProtocol, fetchSampleReport } from "../api/client";
import { LOAD_REPORT_STEPS } from "./AuditProgressOverlay";
import type { AuditReport } from "../types/audit";

interface Props {
  onRunAudit: (
    title: string,
    task: () => Promise<AuditReport>,
    steps?: readonly string[],
  ) => Promise<void>;
  disabled?: boolean;
}

export function FixtureLanding({ onRunAudit, disabled = false }: Props) {
  const [loading, setLoading] = useState<"sample" | "audit" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadSample() {
    setLoading("sample");
    setError(null);
    try {
      await onRunAudit("Pinned sample report", () => fetchSampleReport(), LOAD_REPORT_STEPS);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load sample report");
    } finally {
      setLoading(null);
    }
  }

  async function runDemoAudit() {
    setLoading("audit");
    setError(null);
    try {
      await onRunAudit("Demo protocol audit", async () => {
        const protocol = await fetchDemoProtocol();
        return auditProtocol(protocol);
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Demo audit failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="panel">
      <h2>Demo</h2>
      <p className="footnote">
        Load the pinned sample report or run a live offline audit on{" "}
        <code>protocols/demo.json</code>.
      </p>
      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginTop: "1rem" }}>
        <button type="button" className="btn" disabled={disabled || loading !== null} onClick={() => void loadSample()}>
          Load sample report
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          disabled={disabled || loading !== null}
          onClick={() => void runDemoAudit()}
        >
          Run demo audit
        </button>
      </div>
      {loading && <p className="loading">Starting…</p>}
      {error && <p className="error-box">{error}</p>}
    </div>
  );
}
