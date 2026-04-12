import { Link } from 'react-router-dom'
import Card from '../ui/Card'
import Button from '../ui/Button'

export default function PortfolioEmptyState() {
  return (
    <Card>
      <h3 className="text-base font-semibold text-content mt-0 mb-2">No evaluated projects yet</h3>
      <p className="text-sm text-contentSecondary m-0 mb-4">
        Your portfolio fills in when you complete tasks and your submissions pass automated evaluation. Claim a
        task, submit your work, and return here to see scores and mentor feedback in one place.
      </p>
      <div className="flex flex-wrap gap-2">
        <Link to="/tasks">
          <Button>Go to my tasks</Button>
        </Link>
        <Link to="/assessment">
          <Button variant="secondary">Take assessment</Button>
        </Link>
      </div>
    </Card>
  )
}
