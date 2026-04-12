import Card from '../ui/Card'
import Badge from '../ui/Badge'

function formatScore(v) {
  if (v === null || v === undefined) return '—'
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(2)
  return String(v)
}

export default function EvaluationPanel({ taskType, submission }) {
  if (!submission) return null

  const status = (submission.status || '').toLowerCase()
  const ev = submission.evaluation
  const err = submission.evaluation_error

  const statusLabel =
    status === 'evaluated' ? 'Evaluated' : status === 'failed' ? 'Evaluation failed' : status || 'Unknown'

  return (
    <Card>
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <h3 className="text-lg font-semibold text-content m-0">Evaluation</h3>
        <Badge active={status === 'evaluated'}>{statusLabel}</Badge>
      </div>

      {err && (
        <div className="text-sm text-error mb-3 p-2 rounded-md bg-[rgba(220,80,80,0.08)] border border-borderInput">
          {err}
        </div>
      )}

      {!ev && !err && (
        <p className="text-sm text-contentSecondary m-0">No evaluation payload yet.</p>
      )}

      {ev && (
        <div className="flex flex-col gap-4 text-left">
          <div>
            <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-1">
              Overall score
            </div>
            <div className="text-2xl font-bold text-content">
              {formatScore(ev.overall_score)}
              {ev.overall_score != null && <span className="text-base font-normal text-contentSecondary"> / 100</span>}
            </div>
          </div>

          {ev.score_breakdown && Object.keys(ev.score_breakdown).length > 0 && (
            <div>
              <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-2">
                Score breakdown
              </div>
              <ul className="list-none m-0 p-0 flex flex-col gap-1">
                {Object.entries(ev.score_breakdown).map(([k, v]) => (
                  <li
                    key={k}
                    className="flex justify-between gap-2 text-sm border-b border-borderLight pb-1 last:border-0"
                  >
                    <span className="text-contentSecondary capitalize">{k.replace(/_/g, ' ')}</span>
                    <span className="font-medium text-content">{formatScore(v)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {ev.feedback_summary && (
            <div>
              <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-1">Feedback</div>
              <p className="text-sm text-content m-0 leading-relaxed">{ev.feedback_summary}</p>
            </div>
          )}

          {taskType === 'writing' && ev.details && (
            <div>
              <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-2">
                Writing metrics
              </div>
              <ul className="list-none m-0 p-0 flex flex-col gap-1 text-sm">
                <li className="flex justify-between gap-2">
                  <span className="text-contentSecondary">Word count</span>
                  <span className="text-content">{ev.details.word_count ?? '—'}</span>
                </li>
                {ev.details.min_words != null && (
                  <li className="flex justify-between gap-2">
                    <span className="text-contentSecondary">Target range</span>
                    <span className="text-content">
                      {ev.details.min_words} – {ev.details.max_words} words
                    </span>
                  </li>
                )}
                {ev.details.grammar_issues?.length > 0 && (
                  <li className="text-contentSecondary">
                    Grammar notes: {ev.details.grammar_issues.length} item(s) — see areas for improvement.
                  </li>
                )}
              </ul>
            </div>
          )}

          {taskType === 'programming' && Array.isArray(ev.test_results) && ev.test_results.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-2">
                Test cases ({ev.passed_tests ?? '—'} passed / {ev.test_results.length} run)
              </div>
              <div className="overflow-x-auto rounded-md border border-borderLight">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-primary text-left">
                      <th className="p-2 font-semibold text-content">#</th>
                      <th className="p-2 font-semibold text-content">Name</th>
                      <th className="p-2 font-semibold text-content">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ev.test_results.map((tr, i) => (
                      <tr key={tr.index ?? i} className="border-t border-borderLight align-top">
                        <td className="p-2 text-contentMuted">{i + 1}</td>
                        <td className="p-2 text-content">
                          <div>{tr.name || `Test ${i + 1}`}</div>
                          {!tr.passed && (tr.error || tr.stderr) && (
                            <div className="text-xs text-error mt-1 font-mono whitespace-pre-wrap break-all">
                              {tr.error || tr.stderr}
                            </div>
                          )}
                        </td>
                        <td className="p-2">
                          <Badge active={tr.passed}>{tr.passed ? 'Passed' : 'Failed'}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {taskType === 'design' && (
            <div className="flex flex-col gap-3">
              {typeof ev.mentor_review_required === 'boolean' && (
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-semibold text-contentMuted uppercase tracking-wide">
                    Mentor review
                  </span>
                  <Badge active={ev.mentor_review_required}>
                    {ev.mentor_review_required ? 'Required' : 'Not required'}
                  </Badge>
                </div>
              )}
              {ev.mentor_review_reason && (
                <p className="text-sm text-contentSecondary m-0">{ev.mentor_review_reason}</p>
              )}
              {Array.isArray(ev.automated_checks) && ev.automated_checks.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-2">
                    Automated checks
                  </div>
                  <ul className="list-none m-0 p-0 flex flex-col gap-1">
                    {ev.automated_checks.map((c) => (
                      <li
                        key={c.name}
                        className="flex flex-wrap justify-between gap-2 text-sm border-b border-borderLight pb-1 last:border-0"
                      >
                        <span className="text-content font-medium">{c.name}</span>
                        <Badge active={c.passed}>{c.passed ? 'Pass' : 'Fail'}</Badge>
                        <span className="w-full text-contentSecondary text-xs">{c.detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {Array.isArray(ev.validation_issues) && ev.validation_issues.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-1">
                    Validation issues
                  </div>
                  <ul className="m-0 pl-4 text-sm text-content">
                    {ev.validation_issues.map((x, i) => (
                      <li key={i}>{x}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {ev.strengths?.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-1">Strengths</div>
              <ul className="m-0 pl-4 text-sm text-content">
                {ev.strengths.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}

          {ev.areas_for_improvement?.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-contentMuted uppercase tracking-wide mb-1">
                Areas for improvement
              </div>
              <ul className="m-0 pl-4 text-sm text-content">
                {ev.areas_for_improvement.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Card>
  )
}
