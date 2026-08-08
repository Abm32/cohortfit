interface Props {
  warnings: string[];
}

export function WarningsBanner({ warnings }: Props) {
  if (warnings.length === 0) return null;
  return (
    <section className="warnings-banner" aria-label="Audit warnings">
      <h2>Warnings</h2>
      <ul>
        {warnings.map((w, i) => (
          <li key={i}>{w}</li>
        ))}
      </ul>
    </section>
  );
}
