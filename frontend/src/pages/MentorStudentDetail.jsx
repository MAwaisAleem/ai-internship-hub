import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { mentorApi } from '../api/client'
import { getApiErrorMessage } from '../utils/apiError'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

export default function MentorStudentDetail() {
  const { studentId } = useParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [progress, setProgress] = useState(null)

  useEffect(() => {
    if (!studentId) return
    setLoading(true)
    setError('')
    mentorApi
      .getStudentProgress(studentId)
      .then((res) => setProgress(res.data.progress))
      .catch((err) => setError(getApiErrorMessage(err, 'Failed to load progress')))
      .finally(() => setLoading(false))
  }, [studentId])

  if (loading) {
    return (
      <DashboardLayout title="Student progress" subtitle="Loading…">
        <Card>
          <p className="text-contentSecondary m-0">Loading…</p>
        </Card>
      </DashboardLayout>
    )
  }

  if (error || !progress) {
    return (
      <DashboardLayout title="Student progress" subtitle="">
        <Card>
          <p className="text-error text-sm m-0 mb-2">{error || 'Not found.'}</p>
          <Link to="/mentor?tab=students" className="text-sm text-mint-active">
            ← Back to mentor dashboard
          </Link>
        </Card>
      </DashboardLayout>
    )
  }

  const byStatus = progress.assignments_by_status || {}

  return (
    <DashboardLayout title="Student progress" subtitle={`Student ID: ${progress.student_id}`}>
      <div className="mb-2">
        <Link to="/mentor?tab=students" className="text-sm text-mint-active no-underline hover:underline">
          ← Back to assigned students
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Card>
          <h3 className="text-base font-semibold text-content mt-0 mb-2">Assignments</h3>
          <p className="text-2xl font-bold text-content m-0">{progress.assignments_total}</p>
          <p className="text-xs text-contentSecondary m-0 mt-1">Total task assignments</p>
        </Card>
        <Card>
          <h3 className="text-base font-semibold text-content mt-0 mb-2">Submissions</h3>
          <p className="text-2xl font-bold text-content m-0">{progress.submissions_total}</p>
          <p className="text-xs text-contentSecondary m-0 mt-1">All submission attempts</p>
        </Card>
        <Card>
          <h3 className="text-base font-semibold text-content mt-0 mb-2">Your feedback given</h3>
          <p className="text-2xl font-bold text-content m-0">
            {progress.mentor_reviews_completed_for_this_mentor}
          </p>
          <p className="text-xs text-contentSecondary m-0 mt-1">Completed mentor reviews</p>
        </Card>
      </div>

      <Card>
        <h3 className="text-base font-semibold text-content mt-0 mb-3">Assignments by status</h3>
        {Object.keys(byStatus).length === 0 ? (
          <p className="text-sm text-contentSecondary m-0">No assignment data.</p>
        ) : (
          <ul className="list-none m-0 p-0 flex flex-col gap-1">
            {Object.entries(byStatus).map(([k, v]) => (
              <li key={k} className="flex justify-between text-sm border-b border-borderLight pb-1">
                <span className="text-contentSecondary capitalize">{k}</span>
                <span className="font-medium text-content">{v}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Link to="/mentor?tab=pending">
        <Button variant="secondary">View pending reviews</Button>
      </Link>
    </DashboardLayout>
  )
}
