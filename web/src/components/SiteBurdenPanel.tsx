import type { SiteFinding } from "../types/audit";
import { formatAtRiskRate, formatExpectedN, inferPlannedN } from "../display";
import { SiteBurdenFootnote } from "./SiteBurdenFootnote";

interface Props {
  siteFindings: SiteFinding[];
}

export function SiteBurdenPanel({ siteFindings }: Props) {
  if (siteFindings.length === 0) return null;

  const sorted = [...siteFindings].sort(
    (a, b) => b.at_risk_fraction - a.at_risk_fraction,
  );
  const lowestRate = sorted[sorted.length - 1]?.at_risk_fraction ?? 0;

  return (
    <section className="panel">
      <h2>Site burden</h2>
      <table className="site-table">
        <thead>
          <tr>
            <th>Site</th>
            <th>Gene</th>
            <th>At-risk rate</th>
            <th>Expected at-risk N</th>
            <th>Planned N (inferred)</th>
            <th>Rate ratio vs lowest</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((site) => {
            const ratio =
              lowestRate > 0 ? site.at_risk_fraction / lowestRate : 1;
            return (
              <tr key={`${site.site_name}-${site.gene}`}>
                <td>{site.site_name}</td>
                <td>{site.gene}</td>
                <td>{formatAtRiskRate(site.at_risk_fraction)}</td>
                <td>{formatExpectedN(site.expected_at_risk_n)}</td>
                <td>
                  {inferPlannedN(site.expected_at_risk_n, site.at_risk_fraction)}
                </td>
                <td>{ratio.toFixed(2)}×</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <SiteBurdenFootnote />
    </section>
  );
}
