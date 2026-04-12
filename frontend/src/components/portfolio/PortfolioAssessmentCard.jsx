import Card from '../ui/Card'

export default function PortfolioAssessmentCard({ assessment }) {
  if (!assessment) return null

  const { overall_score, recommended_domain, recommended_domains } = assessment

  return (
    <Card>
      <h3 className="text-base font-semibold text-content mt-0 mb-2">Skill assessment</h3>
      <p className="text-xs text-contentSecondary m-0 mb-3">From your latest MCQ assessment.</p>
      {overall_score != null && (
        <p className="text-sm text-content m-0 mb-2">
          <strong>Overall:</strong> {overall_score}%
        </p>
      )}
      {recommended_domain && (
        <p className="text-sm text-content m-0 mb-2">
          <strong>Recommended focus:</strong> {recommended_domain}
        </p>
      )}
      {recommended_domains && recommended_domains.length > 0 && (
        <p className="text-sm text-contentSecondary m-0">
          Top areas: {recommended_domains.slice(0, 5).join(', ')}
        </p>
      )}
    </Card>
  )
}
