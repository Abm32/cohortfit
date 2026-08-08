interface Props {
  warnings: string[];
  findingsCount: number;
}

export function EmptyFindings({ warnings, findingsCount }: Props) {
  if (findingsCount > 0) return null;

  if (warnings.length > 0) {
    return (
      <div className="empty-state panel">
        <p>Could not compute PGx findings for this protocol.</p>
        <p className="footnote">See warnings above for details.</p>
      </div>
    );
  }

  return (
    <div className="empty-state panel">
      <p>No PGx-actionable drug interactions found in this protocol.</p>
    </div>
  );
}
