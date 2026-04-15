import Card from "../ui/Card";

/**
 * Summary metric for analytics dashboards — uses global theme only.
 */
export default function AnalyticsStatCard({ label, value, hint, sub }) {
  return (
    <Card>
      <p className="text-xs text-contentMuted uppercase tracking-wide m-0 mb-1">{label}</p>
      <p className="text-2xl font-bold text-content m-0">{value}</p>
      {hint ? <p className="text-xs text-contentSecondary m-0 mt-1">{hint}</p> : null}
      {sub ? <p className="text-sm text-contentMuted m-0 mt-1">{sub}</p> : null}
    </Card>
  );
}
