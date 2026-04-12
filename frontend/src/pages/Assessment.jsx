import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { assessmentApi } from '../api/client'
import DashboardLayout from '../components/layout/DashboardLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

export default function Assessment() {
  const [questions, setQuestions] = useState([])
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    assessmentApi
      .getQuestions()
      .then((res) => setQuestions(res.data.questions || []))
      .catch((err) => setError(err.response?.data?.message || 'Failed to load questions'))
      .finally(() => setLoading(false))
  }, [])

  const selectOption = (questionId, index) =>
    setAnswers((prev) => ({ ...prev, [questionId]: index }))

  const handleSubmit = async () => {
    if (questions.filter((q) => answers[q.id] !== undefined).length < questions.length) {
      setError('Please answer all questions')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const payload = questions.map((q) => ({ question_id: q.id, selected_option: answers[q.id] }))
      await assessmentApi.submit(payload)
      navigate('/result', { replace: true })
    } catch (err) {
      setError(err.response?.data?.message || 'Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout title="Skill Assessment" subtitle="Loading...">
        <Card>
          <p className="text-center p-3">Loading assessment...</p>
        </Card>
      </DashboardLayout>
    )
  }

  if (questions.length === 0) {
    return (
      <DashboardLayout title="Skill Assessment" subtitle="No questions available">
        <Card>
          {error && <div className="text-sm text-error mb-2 text-left">{error}</div>}
          <p>No questions available. Run the seed script to add questions.</p>
        </Card>
      </DashboardLayout>
    )
  }

  const q = questions[current]
  const progress = Math.round(((current + 1) / questions.length) * 100)
  const title = `Skill Assessment — Question ${current + 1} of ${questions.length}`
  const subtitle = `${progress}% complete`

  return (
    <DashboardLayout title={title} subtitle={subtitle} showSearch={false}>
      <Card>
        {error && <div className="text-sm text-error mb-2 text-left">{error}</div>}
        <div className="mb-2">
          <Badge>{q?.domain}</Badge>
        </div>
        <h3 className="text-lg font-semibold text-content mb-3">{q?.question}</h3>
        <div className="flex flex-col gap-2 mb-4">
          {q?.options?.map((opt, i) => (
            <button
              key={i}
              type="button"
              onClick={() => selectOption(q.id, i)}
              className={`block w-full text-left py-3 px-3 rounded-card text-base bg-card text-content border-2 transition-colors duration-150 cursor-pointer ${
                answers[q.id] === i
                  ? 'border-mint-active bg-[rgba(125,211,196,0.15)]'
                  : 'border-borderInput hover:border-mint hover:bg-primary'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
        <div className="flex justify-between gap-2 flex-wrap">
          <Button
            variant="secondary"
            onClick={() => setCurrent((c) => Math.max(0, c - 1))}
            disabled={current === 0}
          >
            Previous
          </Button>
          {current < questions.length - 1 ? (
            <Button
              onClick={() => setCurrent((c) => c + 1)}
              disabled={answers[q?.id] === undefined}
            >
              Next
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={answers[q?.id] === undefined || submitting}
            >
              {submitting ? 'Submitting...' : 'Submit'}
            </Button>
          )}
        </div>
      </Card>
    </DashboardLayout>
  )
}
