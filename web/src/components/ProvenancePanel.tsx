import { useState } from "react";
import { fetchProvenance } from "../api/client";
import type { ProvenanceResponse } from "../types/audit";

interface Props {
  gene: string;
}

export function ProvenancePanel({ gene }: Props) {
  const [data, setData] = useState<ProvenanceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  async function handleOpen() {
    if (loaded || loading) return;
    setLoading(true);
    setError(null);
    try {
      setData(await fetchProvenance(gene));
      setLoaded(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load provenance");
    } finally {
      setLoading(false);
    }
  }

  return (
    <details className="panel provenance-panel" onToggle={(e) => {
      if ((e.target as HTMLDetailsElement).open) void handleOpen();
    }}>
      <summary>Frequency provenance — {gene}</summary>
      <div className="provenance-body">
        {loading && <p className="loading">Loading…</p>}
        {error && <p className="error-box">{error}</p>}
        {data && (
          <>
            {data.known_discrepancies.length > 0 && (
              <>
                <h3>Known discrepancies</h3>
                <pre>{JSON.stringify(data.known_discrepancies, null, 2)}</pre>
              </>
            )}
            <h3>Populations</h3>
            <pre>{JSON.stringify(data.populations, null, 2)}</pre>
          </>
        )}
      </div>
    </details>
  );
}
