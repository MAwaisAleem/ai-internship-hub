import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

function StatCard({ label, value, hint }) {
  return (
    <Card>
      <p className="text-xs text-contentMuted uppercase m-0 mb-1">{label}</p>
      <p className="text-2xl font-bold text-content m-0">{value}</p>
      {hint ? <p className="text-xs text-contentSecondary m-0 mt-1">{hint}</p> : null}
    </Card>
  );
}

export default function AdminOverview() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState(null);

  const load = useCallback(async (silent) => {
    setError("");
    if (silent) setRefreshing(true);
    else setLoading(true);
    try {
      const { data } = await adminApi.getReportsSummary();
      setReport(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load admin summary"));
    } finally {
      if (silent) setRefreshing(false);
      else setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(false);
  }, [load]);

  const ov = report?.overview;

  return (
    <DashboardLayout
      title="Admin overview"
      subtitle="Platform summary and quick links for management."
      showSearch={false}
    >
      <div className="flex flex-wrap gap-2 mb-2">
        <Button type="button" variant="secondary" onClick={() => load(true)} disabled={loading || refreshing}>
          {refreshing ? "Refreshing…" : "Refresh"}
        </Button>
        <Link to="/admin/users">
          <Button variant="secondary">Users</Button>
        </Link>
        <Link to="/admin/tasks">
          <Button variant="secondary">Tasks</Button>
        </Link>
        <Link to="/admin/submissions">
          <Button variant="secondary">Submissions</Button>
        </Link>
        <Link to="/admin/roster">
          <Button variant="secondary">Roster</Button>
        </Link>
      </div>

      {error ? (
        <Card>
          <p className="text-sm text-error m-0">{error}</p>
        </Card>
      ) : null}

      {loading ? (
        <Card>
          <p className="text-sm text-contentSecondary text-center m-0 py-4">Loading platform summary…</p>
        </Card>
      ) : null}

      {!loading && ov && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <StatCard label="Total users" value={ov.users_total ?? "—"} />
            <StatCard label="Open tasks" value={ov.tasks_open ?? "—"} hint={`Closed: ${ov.tasks_closed ?? 0}`} />
            <StatCard label="Assignments" value={ov.task_assignments_total ?? "—"} />
            <StatCard label="Submissions" value={ov.submissions_total ?? "—"} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <StatCard
              label="Active roster links"
              value={ov.mentor_roster_links_active ?? "—"}
              hint={`Total links: ${ov.mentor_roster_links_total ?? 0}`}
            />
            <StatCard label="Mentor reviews" value={ov.mentor_reviews_total ?? "—"} />
            <Card>
              <p className="text-xs text-contentMuted uppercase m-0 mb-2">Users by role</p>
              <ul className="text-sm text-content m-0 pl-4 space-y-1">
                {ov.users_by_role &&
                  Object.entries(ov.users_by_role).map(([role, n]) => (
                    <li key={role}>
                      {role}: <strong>{n}</strong>
                    </li>
                  ))}
              </ul>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <Card>
              <h3 className="text-sm font-semibold text-content m-0 mb-2">Assignments by status</h3>
              {report.assignments_by_status?.length ? (
                <table className="w-full text-sm text-content border-collapse">
                  <tbody>
                    {report.assignments_by_status.map((row) => (
                      <tr key={String(row.status)} className="border-b border-borderLight">
                        <td className="py-2 pr-2">{row.status}</td>
                        <td className="py-2 text-right font-medium">{row.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="text-sm text-contentSecondary m-0">No assignment data yet.</p>
              )}
            </Card>
            <Card>
              <h3 className="text-sm font-semibold text-content m-0 mb-2">Submissions by status</h3>
              {report.submissions_by_status?.length ? (
                <table className="w-full text-sm text-content border-collapse">
                  <tbody>
                    {report.submissions_by_status.map((row) => (
                      <tr key={String(row.status)} className="border-b border-borderLight">
                        <td className="py-2 pr-2">{row.status}</td>
                        <td className="py-2 text-right font-medium">{row.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="text-sm text-contentSecondary m-0">No submissions yet.</p>
              )}
            </Card>
          </div>

          <Card>
            <h3 className="text-sm font-semibold text-content m-0 mb-2">Tasks by domain</h3>
            {report.tasks_by_domain?.length ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-content border-collapse min-w-[280px]">
                  <tbody>
                    {report.tasks_by_domain.map((row) => (
                      <tr key={String(row.domain)} className="border-b border-borderLight">
                        <td className="py-2 pr-2">{row.domain}</td>
                        <td className="py-2 text-right font-medium">{row.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-contentSecondary m-0">No tasks in catalog.</p>
            )}
          </Card>
        </>
      )}
    </DashboardLayout>
  );
}
