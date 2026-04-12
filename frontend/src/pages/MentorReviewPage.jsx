import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { mentorApi } from '../api/client'
import { getApiErrorMessage } from '../utils/apiError'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import EvaluationPanel from '../components/submission/EvaluationPanel'
import SubmissionBodyPreview from '../components/mentor/SubmissionBodyPreview'

export default function MentorReviewPage() {
  const { submissionId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [detail, setDetail] = useState(null)
  const [feedback, setFeedback] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')

  const load = useCallback(() => {
    if (!submissionId) {
      setLoading(false)
      setError('Missing submission id.')
      return
    }
    setLoading(true)
    setError('')
    mentorApi
      .getSubmission(submissionId)
      .then((res) => {
        setDetail(res.data)
        const existing = res.data.mentor_review?.feedback
        if (existing) setFeedback(existing)
        else setFeedback('')
      })
      .catch((err) => setError(getApiErrorMessage(err, 'Failed to load submission')))
      .finally(() => setLoading(false))
  }, [submissionId])

  useEffect(() => {
    load()
  }, [load])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitError('')
    if (!feedback.trim()) {
      setSubmitError('Please enter feedback.')
      return
    }
    setSubmitting(true)
    try {
      await mentorApi.submitFeedback(submissionId, feedback.trim())
      navigate('/mentor?tab=history', {
        replace: true,
        state: { mentorNotice: 'Feedback saved. It now appears under Feedback history.' },
      })
    } catch (err) {
      setSubmitError(getApiErrorMessage(err, 'Could not save feedback'))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout title="Review submission" subtitle="Loading…">
        <Card>
          <p className="text-contentSecondary m-0">Loading…</p>
        </Card>
      </DashboardLayout>
    )
  }

  if (error || !detail) {
    return (
      <DashboardLayout title="Review submission" subtitle="">
        <Card>
          <p className="text-error text-sm m-0 mb-2">{error || 'Not found.'}</p>
          <Link to="/mentor?tab=pending" className="text-sm text-mint-active">
            ← Back to mentor dashboard
          </Link>
        </Card>
      </DashboardLayout>
    )
  }

  const { submission, task, student, mentor_review: existingReview } = detail
  const taskType = (task?.task_type || submission.task_type || '').toLowerCase()

  return (
    <DashboardLayout
      title={task?.title || 'Review submission'}
      subtitle={student?.email ? `Student: ${student.name || ''} (${student.email})` : ''}
    >
      <div className="mb-2 flex flex-wrap gap-2">
        <Link to="/mentor?tab=pending" className="text-sm text-mint-active no-underline hover:underline">
          ← Pending reviews
        </Link>
        <Link to="/mentor?tab=history" className="text-sm text-mint-active no-underline hover:underline">
          Feedback history
        </Link>
        {student?.id && (
          <Link
            to={`/mentor/students/${student.id}`}
            className="text-sm text-mint-active no-underline hover:underline"
          >
            Student progress
          </Link>
        )}
      </div>

      <Card>
        <div className="flex flex-wrap gap-2 items-center mb-2">
          <Badge active>{taskType || 'task'}</Badge>
          {submission.status && (
            <span className="text-xs text-contentSecondary capitalize">Status: {submission.status}</span>
          )}
        </div>
        {task?.description && (
          <p className="text-sm text-contentSecondary m-0 mb-2">{task.description}</p>
        )}
      </Card>

      <Card>
        <h3 className="text-lg font-semibold text-content mt-0 mb-2">Submission</h3>
        {submission.student_notes && (
          <p className="text-sm text-contentSecondary m-0 mb-2">
            <strong>Student notes:</strong> {submission.student_notes}
          </p>
        )}
        <SubmissionBodyPreview submission={submission} />
      </Card>

      <EvaluationPanel taskType={taskType} submission={submission} />

      <Card>
        <h3 className="text-lg font-semibold text-content mt-0 mb-2">
          {existingReview ? 'Update feedback' : 'Your feedback'}
        </h3>
        {existingReview?.completed_at && (
          <p className="text-xs text-contentSecondary m-0 mb-2">Last saved: {existingReview.completed_at}</p>
        )}
        {submitError && (
          <p className="text-sm text-error m-0 mb-2 p-2 rounded-md bg-[rgba(220,80,80,0.08)] border border-borderInput">
            {submitError}
          </p>
        )}
        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
          <label htmlFor="mentor-feedback" className="text-sm font-medium text-content">
            Feedback for the student
          </label>
          <textarea
            id="mentor-feedback"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={8}
            placeholder="Strengths, improvements, alignment with the brief…"
            className="w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus resize-y min-h-[160px]"
          />
          <div>
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Saving…' : 'Submit feedback'}
            </Button>
          </div>
        </form>
      </Card>
    </DashboardLayout>
  )
}
