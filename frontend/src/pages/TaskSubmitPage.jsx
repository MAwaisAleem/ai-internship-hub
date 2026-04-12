import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { assignmentsApi, submissionsApi } from '../api/client'
import { getApiErrorMessage } from '../utils/apiError'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import EvaluationPanel from '../components/submission/EvaluationPanel'

export default function TaskSubmitPage() {
  const { assignmentId } = useParams()
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [assignment, setAssignment] = useState(null)
  const [latest, setLatest] = useState(null)
  const [latestLoadError, setLatestLoadError] = useState('')

  const [textBody, setTextBody] = useState('')
  const [codeBody, setCodeBody] = useState('')
  const [file, setFile] = useState(null)
  const [notes, setNotes] = useState('')

  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [justSubmitted, setJustSubmitted] = useState(null)

  const taskType = (assignment?.task?.task_type || '').toLowerCase()

  useEffect(() => {
    setJustSubmitted(null)
    setTextBody('')
    setCodeBody('')
    setFile(null)
    setNotes('')
    setSubmitError('')
    setLatest(null)
    setLatestLoadError('')
  }, [assignmentId])

  useEffect(() => {
    if (!assignmentId) return
    setLoading(true)
    setLoadError('')
    assignmentsApi
      .get(assignmentId)
      .then((res) => setAssignment(res.data.assignment))
      .catch((err) => setLoadError(getApiErrorMessage(err, 'Failed to load assignment')))
      .finally(() => setLoading(false))
  }, [assignmentId])

  useEffect(() => {
    if (!assignmentId) return
    setLatestLoadError('')
    submissionsApi
      .getLatestForAssignment(assignmentId)
      .then((res) => setLatest(res.data.submission))
      .catch((err) => {
        if (err.response?.status === 404) {
          setLatest(null)
          return
        }
        setLatestLoadError(getApiErrorMessage(err, 'Could not load latest submission'))
      })
  }, [assignmentId, justSubmitted])

  const handleSubmitWriting = async (e) => {
    e.preventDefault()
    setSubmitError('')
    if (!textBody.trim()) {
      setSubmitError('Please enter your response.')
      return
    }
    setSubmitting(true)
    try {
      const { data } = await submissionsApi.submitWriting({
        assignment_id: assignmentId,
        text_content: textBody,
      })
      setJustSubmitted(data.submission)
      setTextBody('')
    } catch (err) {
      setSubmitError(getApiErrorMessage(err, 'Submission failed'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleSubmitProgramming = async (e) => {
    e.preventDefault()
    setSubmitError('')
    if (!codeBody.trim()) {
      setSubmitError('Please paste your code.')
      return
    }
    setSubmitting(true)
    try {
      const { data } = await submissionsApi.submitProgramming({
        assignment_id: assignmentId,
        code_content: codeBody,
      })
      setJustSubmitted(data.submission)
    } catch (err) {
      setSubmitError(getApiErrorMessage(err, 'Submission failed'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleSubmitDesign = async (e) => {
    e.preventDefault()
    setSubmitError('')
    if (!file) {
      setSubmitError('Please choose a file (PNG, JPG, or PDF).')
      return
    }
    setSubmitting(true)
    try {
      const { data } = await submissionsApi.submitDesign(assignmentId, file, notes.trim() || undefined)
      setJustSubmitted(data.submission)
      setFile(null)
      setNotes('')
    } catch (err) {
      setSubmitError(getApiErrorMessage(err, 'Upload failed'))
    } finally {
      setSubmitting(false)
    }
  }

  const displaySubmission = justSubmitted || latest
  const title = assignment?.task?.title || 'Task submission'
  const subtitle = assignment?.task?.description || ''

  if (loading) {
    return (
      <DashboardLayout title="Submit work" subtitle="Loading…">
        <Card>
          <p className="text-contentSecondary m-0 p-2">Loading assignment…</p>
        </Card>
      </DashboardLayout>
    )
  }

  if (loadError || !assignment) {
    return (
      <DashboardLayout title="Submit work" subtitle="">
        <Card>
          <p className="text-error text-sm m-0 mb-2">{loadError || 'Assignment not found.'}</p>
          <Link to="/tasks" className="text-sm">
            ← Back to tasks
          </Link>
        </Card>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title={title} subtitle={subtitle}>
      <div className="mb-2">
        <Link to="/tasks" className="text-sm text-mint-active no-underline hover:underline">
          ← Back to tasks
        </Link>
      </div>

      {assignment.task && (
        <Card>
          <div className="flex flex-wrap gap-2 items-center mb-2">
            <Badge active>{(taskType || 'task').replace(/^\w/, (c) => c.toUpperCase())}</Badge>
            {assignment.status && (
              <span className="text-xs text-contentSecondary capitalize">Assignment: {assignment.status}</span>
            )}
          </div>
          {taskType === 'writing' && assignment.task.constraints && (
            <p className="text-xs text-contentSecondary m-0">
              Suggested length: {assignment.task.constraints.min_words ?? '—'} –{' '}
              {assignment.task.constraints.max_words ?? '—'} words (see task brief).
            </p>
          )}
          {taskType === 'programming' && (
            <p className="text-xs text-contentSecondary m-0">
              Language: {assignment.task.constraints?.language || 'python'} (prototype supports Python only).
            </p>
          )}
          {taskType === 'design' && assignment.task.constraints && (
            <p className="text-xs text-contentSecondary m-0">
              Allowed types:{' '}
              {(assignment.task.constraints.allowed_extensions || ['.png', '.jpg', '.jpeg', '.pdf']).join(', ')}
              {assignment.task.constraints.max_file_mb != null && (
                <> · Max size ~{assignment.task.constraints.max_file_mb} MB</>
              )}
            </p>
          )}
        </Card>
      )}

      {latestLoadError && (
        <Card>
          <p className="text-sm text-contentSecondary m-0">{latestLoadError}</p>
        </Card>
      )}

      <Card>
        <h3 className="text-lg font-semibold text-content mt-0 mb-3">Your submission</h3>

        {submitError && (
          <div className="text-sm text-error mb-3 p-2 rounded-md bg-[rgba(220,80,80,0.08)] border border-borderInput">
            {submitError}
          </div>
        )}

        {taskType === 'writing' && (
          <form onSubmit={handleSubmitWriting} className="flex flex-col gap-3 text-left">
            <label className="text-sm font-medium text-content" htmlFor="writing-body">
              Response
            </label>
            <textarea
              id="writing-body"
              value={textBody}
              onChange={(e) => setTextBody(e.target.value)}
              rows={12}
              placeholder="Write your answer here…"
              className="w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus resize-y min-h-[200px]"
            />
            <div>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Submitting…' : 'Submit for evaluation'}
              </Button>
            </div>
          </form>
        )}

        {taskType === 'programming' && (
          <form onSubmit={handleSubmitProgramming} className="flex flex-col gap-3 text-left">
            <label className="text-sm font-medium text-content" htmlFor="code-body">
              Code
            </label>
            <textarea
              id="code-body"
              value={codeBody}
              onChange={(e) => setCodeBody(e.target.value)}
              rows={16}
              placeholder="# Your Python solution"
              spellCheck={false}
              className="w-full py-2 px-3 border border-borderInput rounded-md text-sm font-mono bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus resize-y min-h-[240px]"
            />
            <div>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Submitting…' : 'Run tests & evaluate'}
              </Button>
            </div>
          </form>
        )}

        {taskType === 'design' && (
          <form onSubmit={handleSubmitDesign} className="flex flex-col gap-3 text-left">
            <label className="text-sm font-medium text-content" htmlFor="design-file">
              File
            </label>
            <input
              id="design-file"
              type="file"
              accept=".png,.jpg,.jpeg,.pdf,image/png,image/jpeg,application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="text-sm text-content file:mr-3 file:py-2 file:px-3 file:rounded-md file:border-0 file:bg-mint-active file:text-onMint file:font-semibold"
            />
            <label className="text-sm font-medium text-content" htmlFor="design-notes">
              Notes (optional)
            </label>
            <textarea
              id="design-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="Optional context for your mentor…"
              className="w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus resize-y"
            />
            <div>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Uploading…' : 'Upload & validate'}
              </Button>
            </div>
          </form>
        )}

        {!['writing', 'programming', 'design'].includes(taskType) && (
          <p className="text-sm text-contentSecondary m-0">
            Unknown task type &quot;{taskType}&quot;. Update the task document or contact your instructor.
          </p>
        )}
      </Card>

      {justSubmitted && (
        <Card>
          <p className="text-sm font-medium text-content m-0 mb-1">Latest attempt (just submitted)</p>
          <p className="text-xs text-contentSecondary m-0">
            Submission id: <code className="text-xs bg-primary px-1 rounded">{justSubmitted.id}</code>
          </p>
        </Card>
      )}

      {!justSubmitted && latest && (
        <Card>
          <p className="text-sm font-medium text-content m-0 mb-1">Saved submission on server</p>
          <p className="text-xs text-contentSecondary m-0">
            Submission id: <code className="text-xs bg-primary px-1 rounded">{latest.id}</code>
          </p>
        </Card>
      )}

      {!displaySubmission && !submitting && (
        <Card>
          <p className="text-sm text-contentSecondary m-0">
            No submission yet. Submit above to see automated evaluation here.
          </p>
        </Card>
      )}

      {displaySubmission && (
        <EvaluationPanel taskType={taskType} submission={displaySubmission} />
      )}
    </DashboardLayout>
  )
}
