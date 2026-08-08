export interface MockAuditCardProps {
  label: string;
  badge: string;
  badgeVariant?: "default" | "actionable" | "warning";
  title: string;
  rows: string[];
  footer: string;
  trialId: string;
}

const BADGE_CLASS: Record<NonNullable<MockAuditCardProps["badgeVariant"]>, string> = {
  default: "landing-mock-badge",
  actionable: "landing-mock-badge landing-mock-badge-actionable",
  warning: "landing-mock-badge landing-mock-badge-actionable",
};

export function MockAuditCard({
  label,
  badge,
  badgeVariant = "default",
  title,
  rows,
  footer,
  trialId,
}: MockAuditCardProps) {
  return (
    <div className="landing-mock-card">
      <div className="landing-mock-header">
        <span>COHORTFIT · DEMO</span>
        <span className={BADGE_CLASS[badgeVariant]}>{badge}</span>
      </div>
      <div className="landing-mock-inner">
        <h4>{label}</h4>
        <p className="landing-mock-title">{title}</p>
        {rows.map((row) => (
          <p key={row} className="landing-mock-row-text">
            {row}
          </p>
        ))}
      </div>
      <div className="landing-mock-footer">
        <span>{footer}</span>
        <span>{trialId}</span>
      </div>
    </div>
  );
}
