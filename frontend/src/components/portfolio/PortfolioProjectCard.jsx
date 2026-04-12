import Card from '../ui/Card'
import Badge from '../ui/Badge'

function formatScore(value) {
  if (value === null || value === undefined) return null
  const n = Number(value)
  if (Number.isNaN(n)) return null
  return `${n % 1 === 0 ? n : n.toFixed(1)}/100`
}

function ScoreBreakdown({ breakdown }) {
  if (!breakdown || typeof breakdown !== 'object') return null
  const entries = Object.entries(breakdown).filter(([, v]) => v != null)
  if (entries.length === 0) return null

  return (
    <ul className="mt-2 space-y-1 text-xs text-contentSecondary m-0 pl-4 list-disc">
      {entries.map(([k, v]) => (
        <li key={k}>
          <span className="capitalize">{k.replace(/_/g, ' ')}:</span>{' '}
          {typeof v === 'number' ? (v % 1 === 0 ? v : v.toFixed(1)) : String(v)}
        </li>
      ))}
    </ul>
  )
}

export default function PortfolioProjectCard({ project }) {
  const { task, evaluation, mentor_feedback, completed_at } = project
  const title = task?.title || 'Project'
  const domain = task?.domain
  const tt = (task?.task_type || '').toLowerCase()
  const scoreLabel = evaluation ? formatScore(evaluation.overall_score) : null

  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
        <div className="min-w-0">
          <h3 className="text-lg font-semibold text-content m-0 mb-1">{title}</h3>
          <div className="flex flex-wrap gap-2 items-center">
            {tt && <Badge>{tt}</Badge>}
            {domain && <span className="text-xs text-contentSecondary">{domain}</span>}
            {task?.difficulty && (
              <span className="text-xs text-contentSecondary capitalize">{task.difficulty}</span>
            )}
          </div>
        </div>
        {scoreLabel && (
          <div className="flex flex-col items-end shrink-0">
            <span className="text-xs text-contentMuted uppercase">Auto score</span>
            <span className="text-lg font-bold text-mint-active">{scoreLabel}</span>
          </div>
        )}
      </div>

      {completed_at && (
        <p className="text-xs text-contentMuted m-0 mb-2">Completed: {completed_at}</p>
      )}

      {(evaluation?.feedback_summary ||
        (evaluation?.score_breakdown && Object.keys(evaluation.score_breakdown).length > 0)) && (
        <div className="rounded-md bg-primary border border-borderLight p-3 mb-3">
          <p className="text-xs font-medium text-contentMuted m-0 mb-1">Evaluation summary</p>
          {evaluation?.feedback_summary && (
            <p className="text-sm text-content m-0">{evaluation.feedback_summary}</p>
          )}
          <ScoreBreakdown breakdown={evaluation.score_breakdown} />
        </div>
      )}

      {(evaluation?.strengths?.length > 0 || evaluation?.areas_for_improvement?.length > 0) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
          {evaluation?.strengths?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-contentMuted m-0 mb-1">Strengths</p>
              <ul className="text-sm text-content m-0 pl-4 list-disc space-y-0.5">
                {evaluation.strengths.slice(0, 6).map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
          {evaluation?.areas_for_improvement?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-contentMuted m-0 mb-1">Growth areas</p>
              <ul className="text-sm text-contentSecondary m-0 pl-4 list-disc space-y-0.5">
                {evaluation.areas_for_improvement.slice(0, 6).map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {mentor_feedback?.has_feedback && mentor_feedback.feedback && (
        <div className="rounded-md border border-mint-active/35 bg-mint/30 p-3">
          <p className="text-xs font-medium text-content m-0 mb-1">Mentor feedback</p>
          {mentor_feedback.completed_at && (
            <p className="text-xs text-contentSecondary m-0 mb-2">{mentor_feedback.completed_at}</p>
          )}
          <p className="text-sm text-content whitespace-pre-wrap m-0">{mentor_feedback.feedback}</p>
        </div>
      )}

      {(!mentor_feedback || !mentor_feedback.has_feedback) && (
        <p className="text-xs text-contentMuted m-0 italic">No mentor feedback for this submission yet.</p>
      )}
    </Card>
  )
}
