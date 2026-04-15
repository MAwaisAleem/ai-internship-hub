import { useCallback, useEffect, useState } from "react";
import { adminApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";

const LIMIT = 15;
const selectClass =
  "w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus";

export default function AdminRosterPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [activeOnly, setActiveOnly] = useState(true);

  const [mId, setMId] = useState("");
  const [sId, setSId] = useState("");
  const [creating, setCreating] = useState(false);
  const [createErr, setCreateErr] = useState("");

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const params = { page, limit: LIMIT };
      params.active = activeOnly;
      const { data } = await adminApi.listRoster(params);
      setRows(data.roster || []);
      setTotal(data.total ?? 0);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load roster"));
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [page, activeOnly]);

  useEffect(() => {
    load();
  }, [load]);

  const submitCreate = async (e) => {
    e.preventDefault();
    setCreateErr("");
    setCreating(true);
    try {
      await adminApi.createRoster({ mentor_id: mId.trim(), student_id: sId.trim() });
      setMId("");
      setSId("");
      setPage(1);
      await load();
    } catch (err) {
      setCreateErr(getApiErrorMessage(err, "Could not create link"));
    } finally {
      setCreating(false);
    }
  };

  const toggleActive = async (row, nextActive) => {
    try {
      await adminApi.patchRoster(row.id, { active: nextActive });
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, "Update failed"));
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));

  return (
    <DashboardLayout
      title="Mentor–student roster"
      subtitle="Create links (Mentor + Student roles) and activate/deactivate."
      showSearch={false}
    >
      <Card>
        <h3 className="text-lg font-semibold text-content m-0 mb-3">New link</h3>
        <form onSubmit={submitCreate} className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
          <div>
            <label className="block text-sm font-medium text-content mb-1">Mentor user ID</label>
            <Input value={mId} onChange={(e) => setMId(e.target.value)} placeholder="ObjectId" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-content mb-1">Student user ID</label>
            <Input value={sId} onChange={(e) => setSId(e.target.value)} placeholder="ObjectId" required />
          </div>
          <div className="md:col-span-2 flex flex-col gap-2">
            {createErr ? <p className="text-sm text-error m-0">{createErr}</p> : null}
            <Button type="submit" disabled={creating}>
              {creating ? "Creating…" : "Create link"}
            </Button>
          </div>
        </form>
      </Card>

      <Card className="mb-3">
        <div className="flex flex-wrap gap-3 items-center">
          <label className="text-sm font-medium text-content m-0">Show</label>
          <select className={selectClass + " w-auto min-w-[160px]"} value={activeOnly ? "active" : "all"} onChange={(e) => setActiveOnly(e.target.value === "active")}>
            <option value="active">Active links only</option>
            <option value="all">All links</option>
          </select>
          <Button type="button" variant="secondary" onClick={() => load()}>
            Refresh
          </Button>
        </div>
      </Card>

      {error ? (
        <Card>
          <p className="text-sm text-error m-0">{error}</p>
        </Card>
      ) : null}

      {loading ? (
        <Card>
          <p className="text-sm text-contentSecondary text-center m-0 py-4">Loading roster…</p>
        </Card>
      ) : null}

      {!loading && !error && rows.length === 0 ? (
        <Card>
          <p className="text-sm text-contentSecondary m-0 text-center py-4">No roster rows for this filter.</p>
        </Card>
      ) : null}

      {!loading && rows.length > 0 ? (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm text-content border-collapse min-w-[640px]">
            <thead>
              <tr className="border-b border-borderLight bg-main text-left">
                <th className="py-3 px-4 font-semibold">Mentor</th>
                <th className="py-3 px-4 font-semibold">Student</th>
                <th className="py-3 px-4 font-semibold">Active</th>
                <th className="py-3 px-4 font-semibold">Since</th>
                <th className="py-3 px-4 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-b border-borderLight">
                  <td className="py-2 px-4 max-w-[180px] truncate" title={r.mentor?.email}>
                    {r.mentor?.name || r.mentor?.email || r.mentor_id}
                  </td>
                  <td className="py-2 px-4 max-w-[180px] truncate" title={r.student?.email}>
                    {r.student?.name || r.student?.email || r.student_id}
                  </td>
                  <td className="py-2 px-4">{r.active ? "yes" : "no"}</td>
                  <td className="py-2 px-4 whitespace-nowrap">{r.created_at || "—"}</td>
                  <td className="py-2 px-4">
                    {r.active ? (
                      <Button type="button" variant="secondary" className="text-sm py-1 px-2" onClick={() => toggleActive(r, false)}>
                        Deactivate
                      </Button>
                    ) : (
                      <Button type="button" variant="secondary" className="text-sm py-1 px-2" onClick={() => toggleActive(r, true)}>
                        Activate
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex flex-wrap items-center justify-between gap-2 p-4 border-t border-borderLight">
            <p className="text-xs text-contentSecondary m-0">
              Page {page} of {totalPages} · {total} links
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
