import Card from "../ui/Card";

/**
 * Simple table + optional bar width for domain averages (no chart library).
 */
export default function DomainPerformanceTable({ rows, title = "Domain performance" }) {
  const safe = Array.isArray(rows) ? rows : [];
  const maxScore = Math.max(
    0,
    ...safe.map((r) => (typeof r.average_score === "number" ? r.average_score : 0)),
  );

  return (
    <Card>
      <h3 className="text-sm font-semibold text-content m-0 mb-3">{title}</h3>
      {safe.length === 0 ? (
        <p className="text-sm text-contentSecondary m-0">No domain data yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-content border-collapse min-w-[520px]">
            <thead>
              <tr className="border-b border-borderLight bg-main text-left">
                <th className="py-2 px-3 font-semibold">Domain</th>
                <th className="py-2 px-3 font-semibold">Submissions</th>
                <th className="py-2 px-3 font-semibold">Avg score</th>
                <th className="py-2 px-3 font-semibold min-w-[140px]">Visual</th>
              </tr>
            </thead>
            <tbody>
              {safe.map((row) => {
                const avg = row.average_score;
                const pct = maxScore > 0 && typeof avg === "number" ? Math.round((avg / maxScore) * 100) : 0;
                return (
                  <tr key={row.domain} className="border-b border-borderLight">
                    <td className="py-2 px-3">{row.domain}</td>
                    <td className="py-2 px-3">{row.submissions_count ?? "—"}</td>
                    <td className="py-2 px-3">{avg != null ? `${avg}` : "—"}</td>
                    <td className="py-2 px-3">
                      <div className="h-2 rounded-sm bg-borderLight overflow-hidden">
                        <div
                          className="h-full bg-mint-active rounded-sm transition-[width] duration-300"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
