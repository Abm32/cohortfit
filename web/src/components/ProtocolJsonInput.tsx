import { useState } from "react";
import { auditProtocol } from "../api/client";
import type { AuditReport, Protocol } from "../types/audit";

interface Props {
  onReport: (report: AuditReport) => void;
}

export function ProtocolJsonInput({ onReport }: Props) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAudit() {
    setLoading(true);
    setError(null);
    try {
      const protocol = JSON.parse(text) as Protocol;
      onReport(await auditProtocol(protocol));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid JSON or audit failed");
    } finally {
      setLoading(false);
    }
  }

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setText(String(reader.result ?? ""));
    reader.readAsText(file);
  }

  return (
    <div className="panel">
      <h2>Upload or paste Protocol JSON</h2>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder='{"title": "...", "drugs": [...]}'
      />
      <div style={{ marginTop: "0.75rem" }}>
        <input type="file" accept=".json,application/json" onChange={handleFile} />
      </div>
      <div style={{ marginTop: "0.75rem" }}>
        <button type="button" className="btn" disabled={loading || !text.trim()} onClick={handleAudit}>
          Audit protocol
        </button>
      </div>
      {loading && <p className="loading">Auditing…</p>}
      {error && <p className="error-box">{error}</p>}
    </div>
  );
}
