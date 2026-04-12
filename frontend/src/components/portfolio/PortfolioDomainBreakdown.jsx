import Card from '../ui/Card'

export default function PortfolioDomainBreakdown({ domains }) {
  if (!domains || domains.length === 0) return null

  return (
    <Card>
      <h3 className="text-base font-semibold text-content mt-0 mb-3">Domains and categories</h3>
      <div className="overflow-x-auto rounded-md border border-borderLight">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="bg-primary border-b border-borderLight">
              <th className="p-2 font-semibold text-content">Domain</th>
              <th className="p-2 font-semibold text-content">Projects</th>
              <th className="p-2 font-semibold text-content">Avg. score</th>
            </tr>
          </thead>
          <tbody>
            {domains.map((row) => (
              <tr key={row.domain} className="border-b border-borderLight">
                <td className="p-2 text-content">{row.domain}</td>
                <td className="p-2 text-contentSecondary">{row.completed_count}</td>
                <td className="p-2 text-contentSecondary">
                  {row.avg_score != null ? `${row.avg_score}` : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
