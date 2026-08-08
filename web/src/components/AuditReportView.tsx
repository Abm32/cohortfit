import type { AuditReport } from "../types/audit";
import { DataSourcesPanel } from "./DataSourcesPanel";
import { EmptyFindings } from "./EmptyFindings";
import { FindingCard } from "./FindingCard";
import { ProvenancePanel } from "./ProvenancePanel";
import { ReportHeader } from "./ReportHeader";
import { SiteBurdenPanel } from "./SiteBurdenPanel";
import { WarningsBanner } from "./WarningsBanner";

interface Props {
  report: AuditReport;
}

export function AuditReportView({ report }: Props) {
  const allCitations = report.findings.flatMap((f) => f.citations);
  const tier0Genes = [
    ...new Set(report.findings.filter((f) => f.tier === 0).map((f) => f.gene)),
  ];

  return (
    <>
      <ReportHeader report={report} />
      <WarningsBanner warnings={report.warnings} />
      <EmptyFindings warnings={report.warnings} findingsCount={report.findings.length} />
      {report.findings.map((finding, i) => (
        <section key={`${finding.gene}-${finding.drug}-${finding.tier}-${i}`} className="panel">
          <FindingCard finding={finding} />
        </section>
      ))}
      <SiteBurdenPanel siteFindings={report.site_findings} />
      <DataSourcesPanel sources={report.data_sources} citations={allCitations} />
      {tier0Genes.map((gene) => (
        <ProvenancePanel key={gene} gene={gene} />
      ))}
    </>
  );
}
