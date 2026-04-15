import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";

const LIMIT = 15;
const selectClass =
  "w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus";

export default function AdminSubmissionsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [userFilter, setUserFilter] = useState("");
  const [userInput, setUserInput] = useState("");

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const params = { page, limit: LIMIT };
      if (statusFilter) params.status = statusFilter;
      if (typeFilter) params.task_type = typeFilter;
      if (userFilter.trim()) params.user_id = userFilter.trim();
      const { data } = await adminApi.listSubmissions(params);
      setRows(data.submissions || []);
      setTotal(data.total ?? 0);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load submissions"));
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, typeFilter, userFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));

  return (
    <DashboardLayout title="Submissions" subtitle="Overview with links to full detail." showSearch={false}>
      <Card className="mb-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 items-end">
          <div>
            <label className="block text-sm font-medium text-content mb-1">Status</label>
            <Input value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} placeholder="e.g. evaluated" />
          </div>
          <div>
            <label className="block text-sm font-medium text-content mb-1">Task type</label>
            <select className={selectClass} value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="">Any</option>
              <option value="writing">writing</option>
              <option value="programming">programming</option>
              <option value="design">design</option>
            </select>
          </div>
          <div className="sm:col-span-2 lg:col-span-2">
            <label className="block text-sm font-medium text-content mb-1">Student user ID</label>
            <div className="flex gap-2 flex-wrap">
              <Input value={userInput} onChange={(e) => setUserInput(e.target.value)} placeholder="ObjectId string" />
              <Button
                type="button"
                onClick={() => {
                  setPage(1);
                  setUserFilter(userInput);
                }}
              >
                Apply
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {error ? (
        <Card>
          <p className="text-sm text-error m-0">{error}</p>
        </Card>
      ) : null}

      {loading ? (
        <Card>
          <p className="text-sm text-contentSecondary text-center m-0 py-4">Loading submissions...</p>
        </Card>
      ) : null}

      {!loading && !error && rows.length === 0 ? (
        <Card>
          <p className="text-sm text-contentSecondary m-0 text-center py-4">No submissions match filters.</p>
        </Card>
      ) : null}

      {!loading && rows.length > 0 ? (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm text-content border-collapse min-w-[720px]">
            <thead>
              <tr className="border-b border-borderLight bg-main text-left">
                <th className="py-3 px-4 font-semibold">Created</th>
                <th className="py-3 px-4 font-semibold">Student</th>
                <th className="py-3 px-4 font-semibold">Type</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold">Task</th>
                <th className="py-3 px-4 font-semibold">Detail</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-b border-borderLight">
                  <td className="py-2 px-4 whitespace-nowrap">{row.created_at || "-"}</td>
                  <td className="py-2 px-4 max-w-[140px] truncate" title={row.student?.email}>
                    {row.student?.email || row.user_id}
                  </td>
                  <td className="py-2 px-4">{row.task_type}</td>
                  <td className="py-2 px-4">{row.status}</td>
                  <td className="py-2 px-4 max-w-[160px] truncate" title={row.task?.title}>
                    {row.task?.title || "-"}
                  </td>
                  <td className="py-2 px-4">
                    <Link
                      to={`/admin/submissions/${row.id}`}
                      className="text-mint-active text-sm font-medium no-underline hover:underline"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex flex-wrap items-center justify-between gap-2 p-4 border-t border-borderLight">
            <p className="text-xs text-contentSecondary m-0">
              Page {page} of {totalPages} - {total} submissions
            </p>
            <div className="flex gap-2">
              <Button type="button" variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Previous
              </Button>
              <Button type="button" variant="secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                Next
              </Button>
            </div>
          </div>
        </Card>
      ) : null}
    </DashboardLayout>
  );
}
