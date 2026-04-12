import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { tasksApi } from '../api/client'
import { getApiErrorMessage } from '../utils/apiError'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import TaskCard from '../components/tasks/TaskCard'

const DOMAINS = [
  'All',
  'Graphic Design',
  'Content Writing',
  'Programming',
  'Freelancing',
  'E-Commerce',
  'QuickBooks',
  'AutoCAD',
]

const DIFFICULTIES = ['All', 'beginner', 'intermediate', 'advanced']

const AVAILABILITY = [
  { value: 'all', label: 'All tasks' },
  { value: 'available', label: 'Available to start' },
  { value: 'started', label: 'Already started' },
]

/** Matches backend cap (30) and default page size */
const RECOMMENDED_LIMIT = 20

const filterSelectClassName =
  'w-full py-2 px-3 border border-borderInput rounded-md text-sm bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus'

function taskAvailability(taskId, assignmentByTaskId) {
  const a = assignmentByTaskId[taskId]
  if (!a) return 'available'
  const st = (a.status || '').toLowerCase()
  if (st === 'completed' || st === 'dropped') return 'available'
  return 'started'
}

function mergeLoadErrors(recResult, asgResult) {
  const parts = []
  if (recResult.status === 'rejected') {
    parts.push(getApiErrorMessage(recResult.reason, 'Failed to load recommendations'))
  }
  if (asgResult.status === 'rejected') {
    parts.push(getApiErrorMessage(asgResult.reason, 'Failed to load your assignments'))
  }
  return parts.length ? parts.join(' ') : ''
}

export default function Tasks() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [hasAssessmentContext, setHasAssessmentContext] = useState(true)
  const [recommendations, setRecommendations] = useState([])
  const [assignments, setAssignments] = useState([])
  const [claimingId, setClaimingId] = useState(null)

  const [filterDomain, setFilterDomain] = useState('All')
  const [filterDifficulty, setFilterDifficulty] = useState('All')
  const [filterAvailability, setFilterAvailability] = useState('all')

  const loadData = useCallback(async () => {
    setError('')
    setLoading(true)
    try {
      const results = await Promise.allSettled([
        tasksApi.getRecommended(RECOMMENDED_LIMIT),
        tasksApi.getMyAssignments(),
      ])
      const recResult = results[0]
      const asgResult = results[1]

      if (recResult.status === 'fulfilled') {
        const recRes = recResult.value
        setRecommendations(recRes.data.recommendations || [])
        setHasAssessmentContext(!!recRes.data.has_assessment_context)
      } else {
        setRecommendations([])
        setHasAssessmentContext(true)
      }

      if (asgResult.status === 'fulfilled') {
        setAssignments(asgResult.value.data.assignments || [])
      } else {
        setAssignments([])
      }

      const errMsg = mergeLoadErrors(recResult, asgResult)
      if (errMsg) setError(errMsg)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load tasks'))
      setRecommendations([])
      setAssignments([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const assignmentByTaskId = useMemo(() => {
    const m = {}
    assignments.forEach((a) => {
      if (a.task_id) m[a.task_id] = a
    })
    return m
  }, [assignments])

  const filteredRows = useMemo(() => {
    return recommendations.filter((row) => {
      const t = row.task || {}
      const tid = t.id
      if (filterDomain !== 'All' && t.domain !== filterDomain) return false
      if (filterDifficulty !== 'All' && (t.difficulty || '').toLowerCase() !== filterDifficulty)
        return false

      const av = taskAvailability(tid, assignmentByTaskId)
      if (filterAvailability === 'available' && av !== 'available') return false
      if (filterAvailability === 'started' && av !== 'started') return false

      return true
    })
  }, [
    recommendations,
    filterDomain,
    filterDifficulty,
    filterAvailability,
    assignmentByTaskId,
  ])

  const handleStart = async (taskId) => {
    if (!taskId || typeof taskId !== 'string') return
    setClaimingId(taskId)
    setError('')
    setSuccessMessage('')
    try {
      await tasksApi.claimTask(taskId)
      setSuccessMessage('Task started successfully. This task is now in progress for your account.')
      await loadData()
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not start task'))
    } finally {
      setClaimingId(null)
    }
  }

  const title = 'Recommended tasks'
  const subtitle =
    'Projects matched to your assessment, skill level, and progress.'

  return (
    <DashboardLayout title={title} subtitle={subtitle} showSearch={false}>
      <section className="flex flex-col gap-3">
        <div className="flex flex-wrap items-end gap-3">
          <div className="flex flex-col gap-1 min-w-[140px]">
            <label htmlFor="filter-domain" className="text-xs font-medium text-contentSecondary">
              Domain
            </label>
            <select
              id="filter-domain"
              value={filterDomain}
              onChange={(e) => setFilterDomain(e.target.value)}
              className={filterSelectClassName}
            >
              {DOMAINS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1 min-w-[140px]">
            <label htmlFor="filter-difficulty" className="text-xs font-medium text-contentSecondary">
              Difficulty
            </label>
            <select
              id="filter-difficulty"
              value={filterDifficulty}
              onChange={(e) => setFilterDifficulty(e.target.value)}
              className={filterSelectClassName}
            >
              {DIFFICULTIES.map((d) => (
                <option key={d} value={d}>
                  {d === 'All' ? 'All' : d}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1 min-w-[160px]">
            <label htmlFor="filter-status" className="text-xs font-medium text-contentSecondary">
              Status
            </label>
            <select
              id="filter-status"
              value={filterAvailability}
              onChange={(e) => setFilterAvailability(e.target.value)}
              className={filterSelectClassName}
            >
              {AVAILABILITY.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <Button type="button" variant="secondary" onClick={loadData} disabled={loading}>
            Refresh
          </Button>
        </div>

        {successMessage && !loading && (
          <Card className="border border-borderInput bg-primary">
            <p className="text-sm text-contentSecondary">{successMessage}</p>
          </Card>
        )}

        {!hasAssessmentContext && !loading && (
          <Card className="border border-borderInput bg-primary">
            <p className="text-sm text-contentSecondary">
              Complete the{' '}
              <Link to="/assessment" className="text-mint-active font-medium no-underline hover:underline">
                skill assessment
              </Link>{' '}
              first for personalized match scores. Until then, tasks are shown with neutral ranking.
            </p>
          </Card>
        )}

        {error && (
          <Card className="border border-error/30 bg-card">
            <p className="text-sm text-error">{error}</p>
            <Button type="button" className="mt-2" onClick={loadData}>
              Try again
            </Button>
          </Card>
        )}

        {loading && (
          <Card>
            <p className="text-center text-sm text-contentSecondary py-6">Loading recommended tasks…</p>
          </Card>
        )}

        {!loading && !error && recommendations.length === 0 && (
          <Card>
            <p className="text-center text-sm text-contentSecondary py-6">
              No recommended tasks yet. Ensure the backend has tasks (run{' '}
              <code className="text-xs bg-primary px-1 rounded">python seed_tasks.py</code>
              {' '}from the <code className="text-xs bg-primary px-1 rounded">backend</code> folder) and
              try Refresh.
            </p>
          </Card>
        )}

        {!loading &&
          !error &&
          recommendations.length > 0 &&
          filteredRows.length === 0 && (
            <Card>
              <p className="text-center text-sm text-contentSecondary py-6">
                No tasks match your filters. Try changing domain, difficulty, or status.
              </p>
            </Card>
          )}

        {!loading && !error && filteredRows.length > 0 && (
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
            {filteredRows.map((row) => {
              const t = row.task || {}
              const tid = t.id
              const av = taskAvailability(tid, assignmentByTaskId)
              const started = av === 'started'
              const completed = assignmentByTaskId[tid]?.status?.toLowerCase() === 'completed'

              let disabledReason = ''
              if (completed) disabledReason = 'You already completed this task.'
              else if (started) disabledReason = 'This task is already in progress.'

              return (
                <TaskCard
                  key={tid}
                  title={t.title}
                  domain={t.domain}
                  difficulty={t.difficulty}
                  description={t.description}
                  estimatedHours={t.estimated_hours}
                  reasons={row.reasons}
                  score={row.score}
                  onStart={() => handleStart(tid)}
                  starting={claimingId === tid}
                  disabled={started || completed}
                  disabledReason={disabledReason || undefined}
                />
              )
            })}
          </div>
        )}
      </section>
    </DashboardLayout>
  )
}
