import { useCallback, useEffect, useState } from "react";
import { analyticsApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import AnalyticsStatCard from "../../components/analytics/AnalyticsStatCard";
import DomainPerformanceTable from "../../components/analytics/DomainPerformanceTable";
import StatusBreakdownBars from "../../components/analytics/StatusBreakdownBars";

export default function AdminAnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const { data: body } = await analyticsApi.getAdminSummary();
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

  const usersByRole = data?.users_by_role;
  const sub = data?.submissions;
  const assignStatus = data?.task_assignments_by_status;
  const domains = data?.domain_performance;

  return (
    <DashboardLayout
      title="Platform analytics"
      subtitle="System-wide summary for administration."
      showSearch={false}
    >
      <div className="flex flex-wrap gap-2 mb-2">
        <Button
          type="button"
          variant="secondary"
          onClick={load}
          disabled={loading}
        >
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
          <p className="text-sm text-contentSecondary text-center m-0 py-6">
            Loading platform analytics…
          </p>
        </Card>
      ) : null}

      {!loading && data && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <AnalyticsStatCard
              label="Total users"
              value={data?.users_total ?? "—"}
              hint="All roles"
            />
            <AnalyticsStatCard
              label="Evaluated submissions"
              value={sub?.evaluated_total ?? "—"}
            />
            <AnalyticsStatCard
              label="System avg score"
              value={
                sub?.average_evaluation_score != null
                  ? String(sub.average_evaluation_score)
                  : "—"
              }
              hint="All evaluated submissions"
            />
            <AnalyticsStatCard
              label="Mentor reviews"
              value={data?.mentor_reviews_completed_total ?? "—"}
              hint="Completed reviews"
            />
          </div>

          <Card>
            <h3 className="text-sm font-semibold text-content m-0 mb-3">
              Users by role
            </h3>
            {usersByRole && Object.keys(usersByRole).length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {Object.entries(usersByRole).map(([role, n]) => (
                  <div
                    key={role}
                    className="flex justify-between items-center py-2 px-3 rounded-md bg-primary border border-borderLight"
                  >
                    <span className="text-sm text-content">{role}</span>
                    <span className="text-lg font-semibold text-content">
                      {n}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-contentSecondary m-0">
                No user counts.
              </p>
            )}
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <StatusBreakdownBars
              title="Task assignments by status"
              rows={assignStatus}
            />
            <DomainPerformanceTable
              rows={domains}
              title="Domain performance (system)"
            />
          </div>

          <Card>
            <h3 className="text-sm font-semibold text-content m-0 mb-1">
              System trends
            </h3>
            <p className="text-xs text-contentSecondary m-0">
              Snapshot metrics only. Time-series trends can be added later with
              dated aggregations.
            </p>
          </Card>
        </>
      )}
    </DashboardLayout>
  );
}
