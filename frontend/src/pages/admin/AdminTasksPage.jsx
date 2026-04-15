import { useCallback, useEffect, useState } from "react";
import { adminApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";

const LIMIT = 12;
const selectClass =
  "w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus";

export default function AdminTasksPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tasks, setTasks] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [domainFilter, setDomainFilter] = useState("");

  const [cTitle, setCTitle] = useState("");
  const [cDesc, setCDesc] = useState("");
  const [cDomain, setCDomain] = useState("");
  const [cDifficulty, setCDifficulty] = useState("beginner");
  const [cType, setCType] = useState("programming");
  const [cStatus, setCStatus] = useState("open");
  const [cLanguage, setCLanguage] = useState("python");
  const [creating, setCreating] = useState(false);
  const [createErr, setCreateErr] = useState("");

  const [editTask, setEditTask] = useState(null);
  const [pStatus, setPStatus] = useState("open");
  const [pTitle, setPTitle] = useState("");
  const [patching, setPatching] = useState(false);
  const [patchErr, setPatchErr] = useState("");

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const params = { page, limit: LIMIT };
      if (statusFilter) params.status = statusFilter;
      if (domainFilter.trim()) params.domain = domainFilter.trim();
      const { data } = await adminApi.listTasks(params);
      setTasks(data.tasks || []);
      setTotal(data.total ?? 0);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load tasks"));
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, domainFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const submitCreate = async (e) => {
    e.preventDefault();
    setCreateErr("");
    setCreating(true);
    try {
      const body = {
        title: cTitle.trim(),
        description: cDesc.trim(),
        domain: cDomain.trim(),
        difficulty: cDifficulty,
        task_type: cType,
        status: cStatus,
      };
      if (cType === "programming") body.language = cLanguage || "python";
      await adminApi.createTask(body);
      setCTitle("");
      setCDesc("");
      setCDomain("");
      setPage(1);
      await load();
    } catch (err) {
      setCreateErr(getApiErrorMessage(err, "Create failed"));
    } finally {
      setCreating(false);
    }
  };

  const openEdit = (t) => {
    setPatchErr("");
    setEditTask(t);
    setPStatus(t.status || "open");
    setPTitle(t.title || "");
  };

  const submitPatch = async (e) => {
    e.preventDefault();
    if (!editTask) return;
    setPatchErr("");
    setPatching(true);
    try {
      await adminApi.patchTask(editTask.id, { status: pStatus, title: pTitle.trim() });
      setEditTask(null);
      await load();
    } catch (err) {
      setPatchErr(getApiErrorMessage(err, "Update failed"));
    } finally {
      setPatching(false);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));
  const ta = selectClass + " min-h-[88px] resize-y";

  return (
    <DashboardLayout title="Tasks" subtitle="Catalog: list, create, and update tasks." showSearch={false}>
      <Card>
        <h3 className="text-lg font-semibold text-content m-0 mb-3">Create task</h3>
        <form onSubmit={submitCreate} className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-content mb-1">Title</label>
            <Input value={cTitle} onChange={(e) => setCTitle(e.target.value)} required />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-content mb-1">Description</label>
            <textarea className={ta} value={cDesc} onChange={(e) => setCDesc(e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm font-medium text-content mb-1">Domain</label>
            <Input value={cDomain} onChange={(e) => setCDomain(e.target.value)} placeholder="e.g. Programming" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-content mb-1">Difficulty</label>
            <select className={selectClass} value={cDifficulty} onChange={(e) => setCDifficulty(e.target.value)}>
              <option value="beginner">beginner</option>
              <option value="intermediate">intermediate</option>
              <option value="advanced">advanced</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-content mb-1">Task type</label>
            <select className={selectClass} value={cType} onChange={(e) => setCType(e.target.value)}>
              <option value="programming">programming</option>
              <option value="writing">writing</option>
              <option value="design">design</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-content mb-1">Status</label>
            <select className={selectClass} value={cStatus} onChange={(e) => setCStatus(e.target.value)}>
              <option value="open">open</option>
              <option value="closed">closed</option>
            </select>
          </div>
          {cType === "programming" ? (
            <div>
              <label className="block text-sm font-medium text-content mb-1">Language</label>
              <Input value={cLanguage} onChange={(e) => setCLanguage(e.target.value)} placeholder="python" />
            </div>
          ) : null}
          <div className="md:col-span-2 flex flex-col gap-2">
            {createErr ? <p className="text-sm text-error m-0">{createErr}</p> : null}
            <Button type="submit" disabled={creating}>
              {creating ? "Creating..." : "Create task"}
            </Button>
          </div>
        </form>
      </Card>

      <Card className="mb-3">
        <div className="flex flex-col sm:flex-row flex-wrap gap-3 items-end">
          <div className="w-full sm:w-36">
            <label className="block text-sm font-medium text-content mb-1">Status</label>
            <select className={selectClass} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">Any</option>
              <option value="open">open</option>
              <option value="closed">closed</option>
            </select>
          </div>
          <div className="flex-1 min-w-[140px]">
            <label className="block text-sm font-medium text-content mb-1">Domain contains</label>
            <Input value={domainFilter} onChange={(e) => setDomainFilter(e.target.value)} placeholder="Filter" />
          </div>
          <Button type="button" onClick={() => setPage(1)}>
            Apply filters
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
          <p className="text-sm text-contentSecondary text-center m-0 py-4">Loading tasks...</p>
        </Card>
      ) : null}

      {!loading && !error && tasks.length === 0 ? (
        <Card>
          <p className="text-sm text-contentSecondary m-0 text-center py-4">No tasks match filters.</p>
        </Card>
      ) : null}

      {!loading && tasks.length > 0 ? (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm text-content border-collapse min-w-[640px]">
            <thead>
              <tr className="border-b border-borderLight bg-main text-left">
                <th className="py-3 px-4 font-semibold">Title</th>
                <th className="py-3 px-4 font-semibold">Domain</th>
                <th className="py-3 px-4 font-semibold">Type</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold w-[90px]">Edit</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((t) => (
                <tr key={t.id} className="border-b border-borderLight">
                  <td className="py-2 px-4 max-w-[220px] truncate" title={t.title}>
                    {t.title}
                  </td>
                  <td className="py-2 px-4">{t.domain}</td>
                  <td className="py-2 px-4">{t.task_type || t.type}</td>
                  <td className="py-2 px-4">{t.status}</td>
                  <td className="py-2 px-4">
                    <Button type="button" variant="secondary" className="text-sm py-1 px-2" onClick={() => openEdit(t)}>
                      Edit
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex flex-wrap items-center justify-between gap-2 p-4 border-t border-borderLight">
            <p className="text-xs text-contentSecondary m-0">
              Page {page} of {totalPages} - {total} tasks
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

      {editTask ? (
        <Card>
          <h3 className="text-lg font-semibold text-content m-0 mb-3">Quick update</h3>
          <form onSubmit={submitPatch} className="flex flex-col gap-3 max-w-md">
            <p className="text-xs text-contentMuted m-0">Task ID: {editTask.id}</p>
            <div>
              <label className="block text-sm font-medium text-content mb-1">Title</label>
              <Input value={pTitle} onChange={(e) => setPTitle(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-content mb-1">Status</label>
              <select className={selectClass} value={pStatus} onChange={(e) => setPStatus(e.target.value)}>
                <option value="open">open</option>
                <option value="closed">closed</option>
              </select>
            </div>
            {patchErr ? <p className="text-sm text-error m-0">{patchErr}</p> : null}
            <div className="flex gap-2">
              <Button type="submit" disabled={patching}>
                {patching ? "Saving..." : "Save"}
              </Button>
              <Button type="button" variant="secondary" onClick={() => setEditTask(null)}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      ) : null}
    </DashboardLayout>
  );
}
