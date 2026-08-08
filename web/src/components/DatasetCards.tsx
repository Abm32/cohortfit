import { useEffect, useState } from "react";
import { auditProtocol, fetchProtocolBySlug, fetchProtocolCatalogue } from "../api/client";
import type { AuditReport, ProtocolCard } from "../types/audit";

interface Props {
  onRunAudit: (
    title: string,
    task: () => Promise<AuditReport>,
    steps?: readonly string[],
  ) => Promise<void>;
  disabled?: boolean;
}

/** Verdict-derived accent, so a card previews the shape of its own result. */
function expectTone(expect: string): string {
  if (expect.includes("NO_SIGNAL")) return "ds-tone-clear";
  if (expect.includes("CONTESTED")) return "ds-tone-contested";
  if (expect.includes("warning")) return "ds-tone-warning";
  return "ds-tone-actionable";
}

export function DatasetCards({ onRunAudit, disabled = false }: Props) {
  const [cards, setCards] = useState<ProtocolCard[]>([]);
  const [activeSlug, setActiveSlug] = useState<string | null>(null);
  const [catalogueError, setCatalogueError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchProtocolCatalogue()
      .then((list) => {
        if (!cancelled) setCards(list);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setCatalogueError(e instanceof Error ? e.message : "Could not load catalogue");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function run(card: ProtocolCard) {
    setActiveSlug(card.slug);
    try {
      await onRunAudit(card.demonstrates, async () => {
        const protocol = await fetchProtocolBySlug(card.slug);
        return auditProtocol(protocol);
      });
    } finally {
      setActiveSlug(null);
    }
  }

  if (catalogueError) {
    return (
      <div className="app-panel">
        <p className="error-box">{catalogueError}</p>
      </div>
    );
  }

  return (
    <section className="app-panel ds-section" aria-labelledby="ds-heading">
      <div className="ds-head">
        <h2 id="ds-heading">Pick a protocol</h2>
        <p className="footnote">
          Four pinned protocols, each exercising a different path through the engine.
          Everything runs offline against pinned gnomAD and CPIC tables — no API key,
          no network.
        </p>
      </div>

      <ul className="ds-grid">
        {cards.map((card) => {
          const busy = activeSlug === card.slug;
          return (
            <li key={card.slug}>
              <button
                type="button"
                className={`ds-card ${expectTone(card.expect)}`}
                onClick={() => void run(card)}
                disabled={disabled || activeSlug !== null}
                aria-busy={busy}
              >
                <span className="ds-demonstrates">{card.demonstrates}</span>
                <span className="ds-title">{card.title}</span>
                <span className="ds-meta">
                  <code>{card.trial_id}</code>
                  <span aria-hidden="true"> · </span>
                  {card.cohort}
                </span>
                <span className="ds-detail">{card.detail}</span>
                <span className="ds-foot">
                  <span className="ds-expect">{card.expect}</span>
                  <span className="ds-run">{busy ? "Starting…" : "Run audit →"}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
