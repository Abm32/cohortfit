import { useEffect, useState } from "react";
import { auditProtocol, fetchProtocolBySlug, fetchProtocolCatalogue } from "../api/client";
import type { AuditReport, ProtocolCard } from "../types/audit";

interface Props {
  onReport: (report: AuditReport) => void;
}

/** Verdict-derived accent, so a card previews the shape of its own result. */
function expectTone(expect: string): string {
  if (expect.includes("NO_SIGNAL")) return "ds-tone-clear";
  if (expect.includes("CONTESTED")) return "ds-tone-contested";
  if (expect.includes("warning")) return "ds-tone-warning";
  return "ds-tone-actionable";
}

/**
 * Pinned demo protocols as selectable cards.
 *
 * The catalogue is fetched rather than hardcoded: the reason each fixture
 * exists lives in the API next to the data (see docs/DATASETS.md), so the UI
 * cannot drift out of step with what the fixtures actually demonstrate.
 */
export function DatasetCards({ onReport }: Props) {
  const [cards, setCards] = useState<ProtocolCard[]>([]);
  const [activeSlug, setActiveSlug] = useState<string | null>(null);
  const [catalogueError, setCatalogueError] = useState<string | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

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

  async function run(slug: string) {
    setActiveSlug(slug);
    setRunError(null);
    try {
      const protocol = await fetchProtocolBySlug(slug);
      onReport(await auditProtocol(protocol));
    } catch (e) {
      setRunError(e instanceof Error ? e.message : "Audit failed");
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
                onClick={() => void run(card.slug)}
                disabled={activeSlug !== null}
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
                  <span className="ds-run">{busy ? "Auditing…" : "Run audit →"}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>

      {runError && <p className="error-box">{runError}</p>}
    </section>
  );
}
