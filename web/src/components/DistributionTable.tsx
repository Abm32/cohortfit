import type { PhenotypeCount } from "../types/audit";
import { formatExpectedN, formatFraction } from "../display";

interface Props {
  rows: PhenotypeCount[];
}

export function DistributionTable({ rows }: Props) {
  if (rows.length === 0) return null;
  return (
    <table className="distribution">
      <thead>
        <tr>
          <th>Phenotype</th>
          <th>Fraction</th>
          <th>Expected N</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.phenotype}>
            <td>{row.phenotype}</td>
            <td>{formatFraction(row.fraction)}</td>
            <td>{formatExpectedN(row.expected_n)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
