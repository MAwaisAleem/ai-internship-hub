import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { assessmentApi } from '../api/client'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

export default function Result() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    assessmentApi
      .getResult()
      .then((res) => setResult(res.data.result))
      .catch((err) => setError(err.response?.data?.message || 'Failed to load result'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <DashboardLayout title="Assessment Result" subtitle="Loading...">
        <Card>
          <p className="text-center p-3">Loading result...</p>
        </Card>
      </DashboardLayout>
    )
  }

  if (error || !result) {
    return (
      <DashboardLayout title="Assessment Result" subtitle="No result found">
        <Card>
          <p>{error || 'No assessment result found.'}</p>
          <Link to="/assessment" className="inline-block mt-3">
            <Button>Take Assessment</Button>
          </Link>
        </Card>
      </DashboardLayout>
    )
  }

  const domains = result.domain_scores || result.scores_by_domain || []
  const recommended = result.recommended_domain || result.recommended_domains?.[0] || 'N/A'
  const overall = result.overall_score ?? 0

  return (
    <DashboardLayout title="Assessment Result" subtitle="Your recommended freelancing domain">
      <Card>
        <div className="bg-gradient-to-br from-mint-active to-mint text-onMint p-4 rounded-card mb-4 text-center">
          <div className="text-xl font-bold">Recommended Domain: {recommended}</div>
          <div className="text-lg mt-1 opacity-95">Overall Score: {overall}%</div>
        </div>

        <h3 className="text-base font-semibold text-content mb-2">Scores by Domain</h3>
        <table className="w-full border-collapse mb-4">
          <thead>
            <tr>
              <th className="py-2 text-left font-semibold text-contentSecondary text-sm">Domain</th>
              <th className="py-2 text-left font-semibold text-contentSecondary text-sm">Score</th>
              <th className="py-2 text-left font-semibold text-contentSecondary text-sm">Correct / Total</th>
            </tr>
          </thead>
          <tbody>
            {domains.map((d) => (
              <tr key={d.domain} className="border-b border-borderLight">
                <td className="py-2 text-content text-sm">{d.domain}</td>
                <td className="py-2 text-content text-sm">{d.score}%</td>
                <td className="py-2 text-content text-sm">{d.correct ?? '-'} / {d.total ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="flex justify-between gap-2 flex-wrap">
          <Link to="/dashboard">
            <Button variant="secondary">Back to Dashboard</Button>
          </Link>
          <Link to="/assessment">
            <Button>Retake Assessment</Button>
          </Link>
        </div>
      </Card>
    </DashboardLayout>
  )
}
