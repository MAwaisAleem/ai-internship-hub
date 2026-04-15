import { useCallback, useEffect, useState } from "react";
import { analyticsApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import AnalyticsStatCard from "../../components/analytics/AnalyticsStatCard";

export default function MentorAnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const { data: body } = await analyticsApi.getMentor();
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

  const roster = data?.roster;
  const activity = data?.mentor_feedback_activity;
  const students = roster?.students ?? [];

  return (
    <DashboardLayout
      title="Mentor analytics"
      subtitle="Roster overview, student progress, and your review activity."
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
          <p className="text-sm text-contentSecondary text-center m-0 py-6">Loading analytics…</p>
        </Card>
      ) : null}

      {!loading && data && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <AnalyticsStatCard
              label="Students on roster"
              value={roster?.student_count ?? 0}
            />
            <AnalyticsStatCard
              label="Reviews completed"
              value={activity?.completed_reviews_total ?? 0}
              hint="All time (completed status)"
            />
            <AnalyticsStatCard
              label="Roster assignments (completed)"
              value={roster?.roster_totals?.completed_assignments ?? 0}
              sub={`Pending: ${roster?.roster_totals?.pending_assignments ?? 0}`}
            />
            <AnalyticsStatCard
              label="Avg score (roster)"
              value={
                roster?.roster_average_score_of_averages != null
                  ? String(roster.roster_average_score_of_averages)
                  : "—"
              }
              hint="Mean of per-student averages"
            />
          </div>

          <Card className="overflow-x-auto p-0">
            <div className="p-4 border-b border-borderLight">
              <h3 className="text-sm font-semibold text-content m-0">Per-student summary</h3>
            </div>
            {students.length === 0 ? (
              <p className="text-sm text-contentSecondary m-0 p-4">No students on your roster yet.</p>
            ) : (
              <table className="w-full text-sm text-content border-collapse min-w-[720px]">
                <thead>
                  <tr className="border-b border-borderLight bg-main text-left">
                    <th className="py-3 px-4 font-semibold">Student</th>
                    <th className="py-3 px-4 font-semibold">Completed</th>
                    <th className="py-3 px-4 font-semibold">Pending</th>
                    <th className="py-3 px-4 font-semibold">Evaluated subs</th>
                    <th className="py-3 px-4 font-semibold">Avg score</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((s) => (
                    <tr key={s.student_id} className="border-b border-borderLight">
                      <td className="py-2 px-4">
                        <span className="font-medium text-content">{s.name || s.email || s.student_id}</span>
                        <br />
                        <span className="text-xs text-contentMuted">{s.email}</span>
                      </td>
                      <td className="py-2 px-4">{s.completed_task_assignments ?? 0}</td>
                      <td className="py-2 px-4">{s.pending_task_assignments ?? 0}</td>
                      <td className="py-2 px-4">{s.submissions_evaluated ?? 0}</td>
                      <td className="py-2 px-4">{s.average_evaluation_score ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-content m-0 mb-3">Recent feedback activity</h3>
            {!activity?.recent_reviews?.length ? (
              <p className="text-sm text-contentSecondary m-0">No completed reviews yet.</p>
            ) : (
              <ul className="list-none m-0 p-0 space-y-3">
                {activity.recent_reviews.map((r) => (
                  <li
                    key={r.review_id}
                    className="border-b border-borderLight pb-3 last:border-0 last:pb-0"
                  >
                    <p className="text-xs text-contentMuted m-0 mb-1">
                      {r.completed_at || "—"} · student {r.student_id?.slice?.(0, 8) ?? ""}…
                    </p>
                    <p className="text-sm text-contentSecondary m-0">{r.feedback_preview || "—"}</p>
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
