import { useState } from "react";
import { auditProtocol, fetchDemoProtocol, fetchSampleReport } from "../api/client";
import type { AuditReport } from "../types/audit";
import { AuditReportView } from "./AuditReportView";

interface Props {
  onReport: (report: AuditReport) => void;
}

export function FixtureLanding({ onReport }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadSample() {
    setLoading(true);
    setError(null);
    try {
      onReport(await fetchSampleReport());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load sample report");
    } finally {
      setLoading(false);
    }
  }

  async function runDemoAudit() {
    setLoading(true);
    setError(null);
    try {
      const protocol = await fetchDemoProtocol();
      onReport(await auditProtocol(protocol));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Demo audit failed");
    } finally {
      setLoading(false);
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
        <button type="button" className="btn" disabled={loading} onClick={loadSample}>
          Load sample report
        </button>
        <button type="button" className="btn btn-secondary" disabled={loading} onClick={runDemoAudit}>
          Run demo audit
        </button>
      </div>
      {loading && <p className="loading">Working…</p>}
      {error && <p className="error-box">{error}</p>}
    </div>
  );
}
