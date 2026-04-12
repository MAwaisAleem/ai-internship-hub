import Card from '../ui/Card'

export default function PortfolioHighlightsList({ highlights }) {
  if (!highlights || highlights.length === 0) return null

  return (
    <Card>
      <h3 className="text-base font-semibold text-content mt-0 mb-3">Progress highlights</h3>
      <ul className="list-none m-0 p-0 flex flex-col gap-2">
        {highlights.map((h, i) => (
          <li
            key={i}
            className="flex gap-2 text-sm text-content pl-4 border-l-2 border-mint-active/60"
          >
            <span className="text-mint-active font-medium shrink-0">✓</span>
            <span>{h.text}</span>
          </li>
        ))}
      </ul>
    </Card>
  )
}
