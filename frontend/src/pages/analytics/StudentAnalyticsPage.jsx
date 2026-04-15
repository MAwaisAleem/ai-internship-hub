import { useCallback, useEffect, useState } from "react";
import { analyticsApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import AnalyticsStatCard from "../../components/analytics/AnalyticsStatCard";
import DomainPerformanceTable from "../../components/analytics/DomainPerformanceTable";

export default function StudentAnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const { data: body } = await analyticsApi.getMe();
      setData(body);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load analytics"));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const prog = data?.progress;
  const subs = data?.submissions;
  const domains = data?.domain_performance;
  const trend = data?.mentor_feedback_trend;

  return (
    <DashboardLayout
      title="Analytics"
      subtitle="Your progress, scores, and domain performance."
      showSearch={false}
    >
      <div className="flex flex-wrap gap-2 mb-2">
        <Button type="button" variant="secondary" onClick={load} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </Button>
      </div>

      {error ? (
        <Card>
          <p className="text-sm text-error m-0">{error}</p>
        </Card>
      ) : null}

      {loading && !data ? (
        <Card>
          <p className="text-sm text-contentSecondary text-center m-0 py-6">Loading your analytics…</p>
        </Card>
      ) : null}

      {!loading && data && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <AnalyticsStatCard
              label="Progress"
              value={prog?.total_task_assignments ? `${prog?.percentage ?? 0}%` : "—"}
              hint={
                prog?.total_task_assignments
                  ? `${prog?.completed_task_assignments ?? 0} of ${prog?.total_task_assignments} assignments completed`
                  : "No assignments yet"
              }
            />
            <AnalyticsStatCard
              label="Completed tasks"
              value={prog?.completed_task_assignments ?? 0}
              sub={`Pending: ${prog?.pending_task_assignments ?? 0}`}
            />
            <AnalyticsStatCard
              label="Average score"
              value={subs?.average_evaluation_score != null ? String(subs.average_evaluation_score) : "—"}
              hint={
                subs?.evaluated_count != null
                  ? `Across ${subs.evaluated_count} evaluated submission(s)`
                  : null
              }
            />
            <AnalyticsStatCard
              label="Submissions"
              value={subs?.total ?? 0}
              hint={`Evaluated: ${subs?.evaluated_count ?? 0}`}
            />
          </div>

          <DomainPerformanceTable rows={domains} title="Performance by domain" />

          <Card>
            <h3 className="text-sm font-semibold text-content m-0 mb-3">Mentor feedback trend</h3>
            {!trend?.length ? (
              <p className="text-sm text-contentSecondary m-0">No completed mentor reviews yet.</p>
            ) : (
              <ul className="list-none m-0 p-0 space-y-3">
                {trend.map((item) => (
                  <li
                    key={item.review_id}
                    className="border-b border-borderLight pb-3 last:border-0 last:pb-0"
                  >
                    <p className="text-xs text-contentMuted m-0 mb-1">{item.completed_at || "—"}</p>
                    <p className="text-sm text-contentSecondary m-0">{item.feedback_preview || "—"}</p>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </>
      )}
    </DashboardLayout>
  );
}
