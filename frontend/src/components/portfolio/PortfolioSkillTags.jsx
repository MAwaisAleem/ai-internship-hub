import Card from '../ui/Card'
import Badge from '../ui/Badge'

export default function PortfolioSkillTags({ tags }) {
  if (!tags || tags.length === 0) return null

  return (
    <Card>
      <h3 className="text-base font-semibold text-content mt-0 mb-3">Skills and keywords</h3>
      <p className="text-xs text-contentSecondary m-0 mb-2">
        From your task domains, types, and task metadata.
      </p>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <Badge key={tag}>{tag}</Badge>
        ))}
      </div>
    </Card>
  )
}
