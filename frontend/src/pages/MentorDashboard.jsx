import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams, useLocation } from 'react-router-dom'
import { mentorApi } from '../api/client'
import { getApiErrorMessage } from '../utils/apiError'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'students', label: 'Assigned students' },
  { id: 'pending', label: 'Pending reviews' },
  { id: 'history', label: 'Feedback history' },
]

export default function MentorDashboard() {
  const [searchParams, setSearchParams] = useSearchParams()
  const location = useLocation()
  const navigate = useNavigate()
  const tabParam = searchParams.get('tab') || 'overview'
  const activeTab = TABS.some((t) => t.id === tabParam) ? tabParam : 'overview'

  const setTab = (id) => {
    setSearchParams(id === 'overview' ? {} : { tab: id })
  }

  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [banner, setBanner] = useState('')
  const [error, setError] = useState('')
  const [students, setStudents] = useState([])
  const [pending, setPending] = useState([])
  const [history, setHistory] = useState([])
  const [historyTotal, setHistoryTotal] = useState(0)

  const loadAll = useCallback(async (silent = false) => {
    setError('')
    if (silent) setRefreshing(true)
    else setLoading(true)
    try {
      const [stRes, penRes, histRes] = await Promise.all([
        mentorApi.getStudents(),
        mentorApi.getPendingSubmissions(50),
        mentorApi.getFeedbackHistory({ limit: 50, skip: 0 }),
      ])
      setStudents(stRes.data.students || [])
      setPending(penRes.data.submissions || [])
      setHistory(histRes.data.reviews || [])
      setHistoryTotal(histRes.data.total ?? 0)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load mentor data'))
    } finally {
      if (silent) setRefreshing(false)
      else setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAll(false)
  }, [loadAll])

  useEffect(() => {
    const msg = location.state?.mentorNotice
    if (!msg) return
    setBanner(msg)
    navigate(`${location.pathname}${location.search}`, { replace: true, state: {} })
  }, [location.state, location.pathname, location.search, navigate])

  useEffect(() => {
    if (!banner) return
    const t = setTimeout(() => setBanner(''), 10000)
    return () => clearTimeout(t)
  }, [banner])

  const pendingNeedingMentor = useMemo(
    () => pending.filter((p) => p.mentor_review_required === true).length,
    [pending],
  )

  const title = 'Mentor dashboard'
  const subtitle = 'Review submissions, give feedback, and track student progress.'

  return (
    <DashboardLayout title={title} subtitle={subtitle} showSearch={false}>
      <div className="flex flex-wrap gap-2 mb-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`py-2 px-3 rounded-md text-sm font-medium border transition-colors ${
              activeTab === t.id
                ? 'bg-mint-active text-onMint border-mint-active'
                : 'bg-card text-contentSecondary border-borderInput hover:border-mint-active'
            }`}
          >
            {t.label}
          </button>
        ))}
        <Button
          type="button"
          variant="secondary"
          onClick={() => loadAll(true)}
          disabled={loading || refreshing}
        >
          {refreshing ? 'Refreshing…' : 'Refresh'}
        </Button>
      </div>

      {banner && (
        <Card className="mb-2 border-mint-active/40" role="status">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <p className="text-sm text-content m-0">{banner}</p>
            <button
              type="button"
              className="text-xs text-mint-active shrink-0 hover:underline"
              onClick={() => setBanner('')}
            >
              Dismiss
            </button>
          </div>
        </Card>
      )}

      {error && (
        <Card>
          <p className="text-sm text-error m-0">{error}</p>
        </Card>
      )}

      {loading && (
        <Card>
          <p className="text-sm text-contentSecondary text-center m-0 py-4">Loading mentor data…</p>
        </Card>
      )}

      {activeTab === 'overview' && !loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <Card>
            <p className="text-xs text-contentMuted uppercase m-0 mb-1">Assigned students</p>
            <p className="text-2xl font-bold text-content m-0">{students.length}</p>
          </Card>
          <Card>
            <p className="text-xs text-contentMuted uppercase m-0 mb-1">Pending reviews</p>
            <p className="text-2xl font-bold text-content m-0">{pending.length}</p>
            {pendingNeedingMentor > 0 && (
              <p className="text-xs text-contentSecondary m-0 mt-1">
                {pendingNeedingMentor} flagged for mentor review
              </p>
            )}
          </Card>
          <Card>
            <p className="text-xs text-contentMuted uppercase m-0 mb-1">Completed feedback</p>
            <p className="text-2xl font-bold text-content m-0">{historyTotal}</p>
          </Card>
          <Card>
            <p className="text-xs text-contentMuted uppercase m-0 mb-1">Shortcuts</p>
            <div className="flex flex-col gap-1 mt-2">
              <button type="button" className="text-left text-sm text-mint-active hover:underline" onClick={() => setTab('pending')}>
                Go to pending →
              </button>
              <button type="button" className="text-left text-sm text-mint-active hover:underline" onClick={() => setTab('history')}>
                View history →
              </button>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'students' && !loading && (
        <Card>
          <h2 className="text-lg font-semibold text-content mt-0 mb-3">Assigned students</h2>
          {!students.length ? (
            <p className="text-sm text-contentSecondary m-0">
              No students on your roster yet. Run <code className="text-xs bg-primary px-1 rounded">seed_mentor_roster.py</code> or
              add <code className="text-xs bg-primary px-1 rounded">mentor_roster</code> in MongoDB.
            </p>
          ) : (
            <div className="overflow-x-auto rounded-md border border-borderLight">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="bg-primary border-b border-borderLight">
                    <th className="p-2 font-semibold text-content">Name</th>
                    <th className="p-2 font-semibold text-content">Email</th>
                    <th className="p-2 font-semibold text-content">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((s) => (
                    <tr key={s.id} className="border-b border-borderLight">
                      <td className="p-2 text-content">{s.name || '—'}</td>
                      <td className="p-2 text-contentSecondary">{s.email}</td>
                      <td className="p-2">
                        <Link
                          to={`/mentor/students/${s.id}`}
                          className="text-mint-active font-medium no-underline hover:underline"
                        >
                          View progress
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'pending' && !loading && (
        <Card>
          <h2 className="text-lg font-semibold text-content mt-0 mb-3">Pending reviews</h2>
          <p className="text-sm text-contentSecondary m-0 mb-3">
            Evaluated submissions that do not yet have completed mentor feedback.
          </p>
          {!pending.length ? (
            <p className="text-sm text-contentSecondary m-0">No pending submissions.</p>
          ) : (
            <div className="overflow-x-auto rounded-md border border-borderLight">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="bg-primary border-b border-borderLight">
                    <th className="p-2 font-semibold text-content">Task</th>
                    <th className="p-2 font-semibold text-content">Type</th>
                    <th className="p-2 font-semibold text-content">Mentor review</th>
                    <th className="p-2 font-semibold text-content">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {pending.map((row) => (
                    <tr key={row.id} className="border-b border-borderLight">
                      <td className="p-2 text-content">{row.task?.title || '—'}</td>
                      <td className="p-2">
                        <Badge>{row.task_type || '—'}</Badge>
                      </td>
                      <td className="p-2">
                        {row.mentor_review_required ? (
                          <Badge active>Required</Badge>
                        ) : (
                          <span className="text-contentSecondary">—</span>
                        )}
                      </td>
                      <td className="p-2">
                        <Link
                          to={`/mentor/submissions/${row.id}`}
                          className="text-mint-active font-medium no-underline hover:underline"
                        >
                          Review
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'history' && !loading && (
        <Card>
          <h2 className="text-lg font-semibold text-content mt-0 mb-3">Feedback history (reviewed submissions)</h2>
          {!history.length ? (
            <p className="text-sm text-contentSecondary m-0">No completed feedback yet.</p>
          ) : (
            <div className="overflow-x-auto rounded-md border border-borderLight">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="bg-primary border-b border-borderLight">
                    <th className="p-2 font-semibold text-content">Student</th>
                    <th className="p-2 font-semibold text-content">Task</th>
                    <th className="p-2 font-semibold text-content">Completed</th>
                    <th className="p-2 font-semibold text-content">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((r) => (
                    <tr key={r.id} className="border-b border-borderLight">
                      <td className="p-2 text-content">{r.student?.name || r.student?.email || '—'}</td>
                      <td className="p-2 text-contentSecondary">
                        {r.submission_summary?.task?.title || '—'}
                      </td>
                      <td className="p-2 text-contentSecondary text-xs">
                        {r.completed_at || '—'}
                      </td>
                      <td className="p-2">
                        <Link
                          to={`/mentor/submissions/${r.submission_id}`}
                          className="text-mint-active font-medium no-underline hover:underline"
                        >
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </DashboardLayout>
  )
}
