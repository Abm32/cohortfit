import { useState } from "react";
import {
  auditProtocol,
  extractProtocol,
  isExtractUnavailableError,
} from "../api/client";
import type { AuditReport } from "../types/audit";

const EXTRACT_STEPS = [
  "Sending prose to Claude extractor",
  "Validating Protocol schema",
  "Running offline audit engine",
  "Assembling tier-labelled report",
] as const;

interface Props {
  onRunAudit: (
    title: string,
    task: () => Promise<AuditReport>,
    steps?: readonly string[],
  ) => Promise<void>;
  disabled?: boolean;
}

export function ProtocolProseInput({ onRunAudit, disabled = false }: Props) {
  const [prose, setProse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [extractDisabled, setExtractDisabled] = useState(false);

  async function handleExtractAndAudit() {
    setLoading(true);
    setError(null);
    try {
      await onRunAudit(
        "Extracted protocol audit",
        async () => {
          const protocol = await extractProtocol(prose);
          return auditProtocol(protocol);
        },
        EXTRACT_STEPS,
      );
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
        disabled={extractDisabled || disabled || loading}
      />
      <div style={{ marginTop: "0.75rem" }}>
        <button
          type="button"
          className="btn"
          disabled={disabled || loading || extractDisabled || !prose.trim()}
          onClick={() => void handleExtractAndAudit()}
        >
          Extract &amp; audit
        </button>
      </div>
      {extractDisabled && (
        <p className="error-box">
          Extraction unavailable — ANTHROPIC_API_KEY is not set on the server.
        </p>
      )}
      {loading && <p className="loading">Starting…</p>}
      {error && !extractDisabled && <p className="error-box">{error}</p>}
    </div>
  );
}
