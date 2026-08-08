import { useState } from "react";
import {
  auditProtocol,
  extractProtocol,
  isExtractUnavailableError,
} from "../api/client";
import type { AuditReport } from "../types/audit";

interface Props {
  onReport: (report: AuditReport) => void;
}

export function ProtocolProseInput({ onReport }: Props) {
  const [prose, setProse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [extractDisabled, setExtractDisabled] = useState(false);

  async function handleExtractAndAudit() {
    setLoading(true);
    setError(null);
    try {
      const protocol = await extractProtocol(prose);
      onReport(await auditProtocol(protocol));
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Extraction failed";
      if (isExtractUnavailableError(msg)) {
        setExtractDisabled(true);
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      <h2>Extract from protocol prose</h2>
      <p className="footnote">
        Requires <code>ANTHROPIC_API_KEY</code> on the server. Claude extracts
        structure only; the audit engine computes all numbers.
      </p>
      <textarea
        value={prose}
        onChange={(e) => setProse(e.target.value)}
        placeholder="Paste protocol text or ClinicalTrials.gov export…"
        disabled={extractDisabled}
      />
      <div style={{ marginTop: "0.75rem" }}>
        <button
          type="button"
          className="btn"
          disabled={loading || extractDisabled || !prose.trim()}
          onClick={handleExtractAndAudit}
        >
          Extract &amp; audit
        </button>
      </div>
      {extractDisabled && (
        <p className="error-box">
          Extraction unavailable — ANTHROPIC_API_KEY is not set on the server.
        </p>
      )}
      {loading && <p className="loading">Extracting and auditing…</p>}
      {error && !extractDisabled && <p className="error-box">{error}</p>}
    </div>
  );
}
