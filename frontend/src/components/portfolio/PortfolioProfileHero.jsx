import Card from '../ui/Card'

export default function PortfolioProfileHero({ profile, summaryLine }) {
  const name = profile?.name || profile?.email || 'Student'
  const initial = (name || '?').charAt(0).toUpperCase()

  return (
    <Card className="border border-borderLight">
      <div className="flex flex-wrap gap-4 items-start">
        <div
          className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-mint-active text-xl font-bold text-onMint"
          aria-hidden
        >
          {initial}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium uppercase tracking-wide text-contentMuted m-0 mb-1">Portfolio</p>
          <h2 className="text-xl font-bold text-content m-0 mb-1">{name}</h2>
          {profile?.email && <p className="text-sm text-contentSecondary m-0 mb-2">{profile.email}</p>}
          {summaryLine && (
            <p className="text-sm text-content leading-relaxed m-0 max-w-3xl border-l-2 border-mint-active pl-3">
              {summaryLine}
            </p>
          )}
        </div>
      </div>
    </Card>
  )
}
