import { useCallback, useEffect, useState } from "react";
import { adminApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";

const ROLES = ["Student", "Mentor", "Administrator"];
const LIMIT = 15;

const selectClass =
  "w-full py-2 px-3 border border-borderInput rounded-md text-base bg-card text-content focus:outline-none focus:border-mint-active focus:ring-2 focus:ring-focus";

export default function AdminUsersPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [roleFilter, setRoleFilter] = useState("");
  const [q, setQ] = useState("");
  const [qInput, setQInput] = useState("");

  const [editUser, setEditUser] = useState(null);
  const [formName, setFormName] = useState("");
  const [formEmail, setFormEmail] = useState("");
  const [formRole, setFormRole] = useState("Student");
  const [formPassword, setFormPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");

  const load = useCallback(async () => {
    setError("");
    setLoading(true);
    try {
      const params = { page, limit: LIMIT };
      if (roleFilter) params.role = roleFilter;
      if (q.trim()) params.q = q.trim();
      const { data } = await adminApi.listUsers(params);
      setUsers(data.users || []);
      setTotal(data.total ?? 0);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load users"));
      setUsers([]);
    } finally {
      setLoading(false);
    }
  }, [page, roleFilter, q]);

  useEffect(() => {
    load();
  }, [load]);

  const openEdit = (u) => {
    setFormError("");
    setEditUser(u);
    setFormName(u.name || "");
    setFormEmail(u.email || "");
    setFormRole(u.role || "Student");
    setFormPassword("");
  };

  const closeEdit = () => {
    setEditUser(null);
    setFormPassword("");
    setFormError("");
  };

  const submitEdit = async (e) => {
    e.preventDefault();
    if (!editUser) return;
    setFormError("");
    setSaving(true);
    try {
      const body = {
        name: formName.trim(),
        email: formEmail.trim().toLowerCase(),
        role: formRole,
      };
      if (formPassword.trim()) body.password = formPassword.trim();
      await adminApi.patchUser(editUser.id, body);
      await load();
      closeEdit();
    } catch (err) {
      setFormError(getApiErrorMessage(err, "Update failed"));
    } finally {
      setSaving(false);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));

  return (
    <DashboardLayout title="Users" subtitle="Search, filter, and update accounts (whitelisted fields only)." showSearch={false}>
      <Card className="mb-3">
        <div className="flex flex-col sm:flex-row flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[160px]">
            <label className="block text-sm font-medium text-content mb-1">Search (name or email)</label>
            <Input value={qInput} onChange={(e) => setQInput(e.target.value)} placeholder="e.g. @student" />
          </div>
          <div className="w-full sm:w-40">
            <label className="block text-sm font-medium text-content mb-1">Role</label>
            <select className={selectClass} value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
              <option value="">All roles</option>
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <Button
            type="button"
            onClick={() => {
              setPage(1);
              setQ(qInput);
            }}
          >
            Apply
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
          <p className="text-sm text-contentSecondary text-center m-0 py-4">Loading users…</p>
        </Card>
      ) : null}

      {!loading && !error && users.length === 0 ? (
        <Card>
          <p className="text-sm text-contentSecondary m-0 text-center py-4">No users match your filters.</p>
        </Card>
      ) : null}

      {!loading && users.length > 0 ? (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm text-content border-collapse min-w-[520px]">
            <thead>
              <tr className="border-b border-borderLight bg-main text-left">
                <th className="py-3 px-4 font-semibold">Email</th>
                <th className="py-3 px-4 font-semibold">Name</th>
                <th className="py-3 px-4 font-semibold">Role</th>
                <th className="py-3 px-4 font-semibold w-[100px]">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-borderLight">
                  <td className="py-2 px-4">{u.email}</td>
                  <td className="py-2 px-4">{u.name}</td>
                  <td className="py-2 px-4">{u.role}</td>
                  <td className="py-2 px-4">
                    <Button type="button" variant="secondary" className="text-sm py-1 px-2" onClick={() => openEdit(u)}>
                      Edit
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex flex-wrap items-center justify-between gap-2 p-4 border-t border-borderLight">
            <p className="text-xs text-contentSecondary m-0">
              Page {page} of {totalPages} · {total} users
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

      {editUser ? (
        <Card>
          <h3 className="text-lg font-semibold text-content m-0 mb-3">Edit user</h3>
          <form onSubmit={submitEdit} className="flex flex-col gap-3 max-w-md">
            <div>
              <label className="block text-sm font-medium text-content mb-1">Name</label>
              <Input value={formName} onChange={(e) => setFormName(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-content mb-1">Email</label>
              <Input type="email" value={formEmail} onChange={(e) => setFormEmail(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-content mb-1">Role</label>
              <select className={selectClass} value={formRole} onChange={(e) => setFormRole(e.target.value)}>
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-content mb-1">New password (optional)</label>
              <Input
                type="password"
                value={formPassword}
                onChange={(e) => setFormPassword(e.target.value)}
                placeholder="Leave blank to keep current"
                autoComplete="new-password"
              />
              <p className="text-xs text-contentMuted m-0 mt-1">Must meet registration rules if set.</p>
            </div>
            {formError ? <p className="text-sm text-error m-0">{formError}</p> : null}
            <div className="flex gap-2">
              <Button type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save changes"}
              </Button>
              <Button type="button" variant="secondary" onClick={closeEdit}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      ) : null}
    </DashboardLayout>
  );
}
