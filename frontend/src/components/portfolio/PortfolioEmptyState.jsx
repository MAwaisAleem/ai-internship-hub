import { Link } from 'react-router-dom'
import Card from '../ui/Card'
import Button from '../ui/Button'

export default function PortfolioEmptyState() {
  return (
    <Card>
      <h3 className="text-base font-semibold text-content mt-0 mb-2">No evaluated projects yet</h3>
      <p className="text-sm text-contentSecondary m-0 mb-4">
        Complete tasks and submit work so automated evaluation can run. Your portfolio will list scores and mentor
        feedback here.
      </p>
      <div className="flex flex-wrap gap-2">
        <Link to="/dashboard">
          <Button variant="secondary">Back to dashboard</Button>
        </Link>
        <Link to="/assessment">
          <Button variant="secondary">Take assessment</Button>
        </Link>
      </div>
    </Card>
  )
}
