import { usePortfolio } from '../hooks/usePortfolio'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import PortfolioProfileHero from '../components/portfolio/PortfolioProfileHero'
import PortfolioSkillTags from '../components/portfolio/PortfolioSkillTags'
import PortfolioDomainBreakdown from '../components/portfolio/PortfolioDomainBreakdown'
import PortfolioHighlightsList from '../components/portfolio/PortfolioHighlightsList'
import PortfolioAssessmentCard from '../components/portfolio/PortfolioAssessmentCard'
import PortfolioProjectCard from '../components/portfolio/PortfolioProjectCard'
import PortfolioEmptyState from '../components/portfolio/PortfolioEmptyState'

export default function PortfolioPage() {
  const { data, loading, error, reload } = usePortfolio()

  if (loading) {
    return (
      <DashboardLayout title="Portfolio" subtitle="Preparing your freelancing profile…" showSearch={false}>
        <Card>
          <p className="text-center py-8 text-contentSecondary m-0">Loading your portfolio…</p>
        </Card>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout title="Portfolio" subtitle="" showSearch={false}>
        <Card>
          <p className="text-sm text-error m-0 mb-3">{error}</p>
          <Button type="button" variant="secondary" onClick={() => reload()}>
            Retry
          </Button>
        </Card>
      </DashboardLayout>
    )
  }

  const profile = data?.profile
  const readiness = data?.readiness || {}
  const projects = data?.projects || []
  const hasProjects = projects.length > 0

  return (
    <DashboardLayout
      title="Portfolio"
      subtitle="Showcase evaluated work, skills, and mentor feedback for freelancing readiness."
      showSearch={false}
    >
      <PortfolioProfileHero profile={profile} summaryLine={readiness.summary_line} />

      <PortfolioAssessmentCard assessment={data?.assessment} />

      <PortfolioHighlightsList highlights={data?.highlights} />

      <PortfolioDomainBreakdown domains={readiness.domains} />

      <PortfolioSkillTags tags={readiness.skill_tags} />

      {!hasProjects && <PortfolioEmptyState />}

      {hasProjects && (
        <>
          <h2 className="text-lg font-semibold text-content m-0">Completed projects</h2>
          <div className="flex flex-col gap-3">
            {projects.map((p) => (
              <PortfolioProjectCard key={p.submission_id || p.assignment_id} project={p} />
            ))}
          </div>
        </>
      )}

      {data?.meta?.generated_at && (
        <p className="text-xs text-contentMuted m-0 text-center">
          Generated {data.meta.generated_at}
          {data.meta.version != null ? ` · v${data.meta.version}` : ''}
        </p>
      )}
    </DashboardLayout>
  )
}
