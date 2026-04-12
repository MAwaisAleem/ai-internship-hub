import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { assignmentsApi } from '../api/client'
import { getApiErrorMessage } from '../utils/apiError'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

function taskTypeBadge(tt) {
  const t = (tt || '').toLowerCase()
  if (t === 'writing') return 'Writing'
  if (t === 'programming') return 'Programming'
  if (t === 'design') return 'Design'
  return tt || 'Task'
}

export default function TasksPage() {
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    assignmentsApi
      .list()
      .then((res) => setAssignments(res.data.assignments || []))
      .catch((err) => setError(getApiErrorMessage(err, 'Failed to load tasks')))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <DashboardLayout title="My tasks" subtitle="Loading your assignments…">
        <Card>
          <p className="text-center p-3 text-contentSecondary m-0">Loading…</p>
        </Card>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout
      title="My tasks"
      subtitle="Open a claimed assignment to submit your work and view evaluation."
    >
      {error && (
        <Card>
          <p className="text-sm text-error m-0">{error}</p>
        </Card>
      )}

      {!error && assignments.length === 0 && (
        <Card>
          <p className="text-sm text-contentSecondary m-0 mb-2">
            No task assignments yet. For testing, run the backend seed scripts with STUDENT_EMAIL in .env
            (seed_writing_task.py, seed_programming_task.py, seed_design_task.py).
          </p>
        </Card>
      )}

      <div className="flex flex-col gap-3">
        {assignments.map((a) => {
          const tt = a.task?.task_type
          const title = a.task?.title || 'Untitled task'
          return (
            <Card key={a.id}>
              <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                <div>
                  <h3 className="text-lg font-semibold text-content m-0 mb-1">{title}</h3>
                  <div className="flex flex-wrap gap-2 items-center">
                    <Badge>{taskTypeBadge(tt)}</Badge>
                    {a.status && (
                      <span className="text-xs text-contentSecondary capitalize">Status: {a.status}</span>
                    )}
                  </div>
                </div>
                <Link to={`/tasks/${a.id}/submit`}>
                  <Button>Submit / view</Button>
                </Link>
              </div>
              {a.task?.description && (
                <p className="text-sm text-contentSecondary m-0">{a.task.description}</p>
              )}
            </Card>
          )
        })}
      </div>
    </DashboardLayout>
  )
}
