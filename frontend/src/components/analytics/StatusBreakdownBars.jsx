import Card from "../ui/Card";

/** Horizontal bars for status counts (admin / system summaries). */
export default function StatusBreakdownBars({ rows, title }) {
  const safe = Array.isArray(rows) ? rows : [];
  const maxCount = Math.max(0, ...safe.map((r) => Number(r.count) || 0));

  return (
    <Card>
      <h3 className="text-sm font-semibold text-content m-0 mb-3">{title}</h3>
      {safe.length === 0 ? (
        <p className="text-sm text-contentSecondary m-0">No data.</p>
      ) : (
        <ul className="list-none m-0 p-0 space-y-3">
          {safe.map((row) => {
            const c = Number(row.count) || 0;
            const pct = maxCount > 0 ? Math.round((c / maxCount) * 100) : 0;
            return (
              <li key={String(row.status)}>
                <div className="flex justify-between text-sm text-content mb-1">
                  <span className="capitalize">{row.status ?? "—"}</span>
                  <span className="font-medium">{c}</span>
                </div>
                <div className="h-2 rounded-sm bg-borderLight overflow-hidden">
                  <div
                    className="h-full bg-mint-active rounded-sm"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
