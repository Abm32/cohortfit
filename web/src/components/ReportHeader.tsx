import type { AuditReport } from "../types/audit";

interface Props {
  report: AuditReport;
}

export function ReportHeader({ report }: Props) {
  return (
    <header className="panel">
      <h1>{report.protocol_title}</h1>
      <div className="meta-row">
        {report.trial_id && <span>Trial: {report.trial_id}</span>}
        <span>Planned N: {report.total_planned_n}</span>
        <span>{report.offline ? "Offline (pinned fixtures)" : "Live frequencies"}</span>
      </div>
    </header>
  );
}
