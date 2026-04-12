import Card from '../ui/Card'
import Button from '../ui/Button'
import Badge from '../ui/Badge'

/**
 * Student task card — uses global theme tokens only.
 */
export default function TaskCard({
  title,
  domain,
  difficulty,
  description,
  estimatedHours,
  reasons,
  score,
  onStart,
  starting = false,
  disabled = false,
  disabledReason,
}) {
  const primaryReasons = (reasons || []).filter((r) => r?.code !== 'SCORE_SUMMARY')

  return (
    <Card className="flex flex-col h-full">
      <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
        <h3 className="text-lg font-semibold text-content leading-snug">{title}</h3>
        <div className="flex flex-wrap gap-1 justify-end">
          {domain && (
            <Badge>{domain}</Badge>
          )}
          {difficulty && (
            <span className="inline-block py-1 px-2 rounded-sm text-xs font-medium bg-primary text-content capitalize border border-borderInput">
              {difficulty}
            </span>
          )}
        </div>
      </div>

      {description && (
        <p className="text-sm text-contentSecondary mb-3 flex-1 max-h-[4.5rem] overflow-hidden">{description}</p>
      )}

      <div className="text-xs text-contentMuted mb-2">
        {estimatedHours != null && estimatedHours !== '' ? (
          <span>Estimated: ~{estimatedHours} h</span>
        ) : (
          <span>Duration: not specified</span>
        )}
        {score != null && (
          <span className="ml-2">· Match: {typeof score === 'number' ? score.toFixed(0) : score}%</span>
        )}
      </div>

      {primaryReasons.length > 0 && (
        <div className="mb-3 p-2 rounded-md bg-primary border border-borderLight">
          <p className="text-xs font-semibold text-content mb-1">Why recommended</p>
          <ul className="text-xs text-contentSecondary space-y-1 list-disc list-inside">
            {primaryReasons.slice(0, 5).map((r, i) => (
              <li key={`${r.code}-${i}`}>{r.message}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-auto pt-1">
        <Button
          type="button"
          onClick={onStart}
          disabled={disabled || starting}
          className="w-full sm:w-auto"
        >
          {starting ? 'Starting…' : 'Start task'}
        </Button>
        {disabled && disabledReason && (
          <p className="text-xs text-contentMuted mt-2">{disabledReason}</p>
        )}
      </div>
    </Card>
  )
}
