import { pubmedUrl } from "../display";

interface Props {
  sources: string[];
  citations: string[];
}

export function DataSourcesPanel({ sources, citations }: Props) {
  const uniqueCitations = [...new Set(citations)];

  return (
    <section className="panel">
      <h2>Data sources</h2>
      <ul className="notes-list">
        {sources.map((src, i) => (
          <li key={i}>{src}</li>
        ))}
      </ul>
      {uniqueCitations.length > 0 && (
        <>
          <h3>Citations</h3>
          <p>
            {uniqueCitations.map((pmid, i) => (
              <span key={pmid}>
                {i > 0 && ", "}
                <a href={pubmedUrl(pmid)} target="_blank" rel="noreferrer">
                  PMID {pmid}
                </a>
              </span>
            ))}
          </p>
        </>
      )}
    </section>
  );
}
