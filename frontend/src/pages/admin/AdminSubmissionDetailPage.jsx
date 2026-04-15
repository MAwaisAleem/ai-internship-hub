import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { adminApi } from "../../api/client";
import { getApiErrorMessage } from "../../utils/apiError";
import DashboardLayout from "../../components/layout/DashboardLayout";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

function JsonBlock({ label, data }) {
  return (
    <Card>
      <h3 className="text-sm font-semibold text-content m-0 mb-2">{label}</h3>
      <pre className="text-xs text-contentSecondary m-0 overflow-x-auto whitespace-pre-wrap break-words max-h-[320px] overflow-y-auto">
        {JSON.stringify(data, null, 2)}
      </pre>
    </Card>
  );
}

export default function AdminSubmissionDetailPage() {
  const { submissionId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setError("");
      setLoading(true);
      try {
        const { data } = await adminApi.getSubmission(submissionId);
        if (!cancelled) setDetail(data);
      } catch (err) {
        if (!cancelled) setError(getApiErrorMessage(err, "Failed to load submission"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [submissionId]);

  return (
    <DashboardLayout title="Submission detail" subtitle="Administrator read-only view." showSearch={false}>
      <div className="mb-3">
        <Link to="/admin/submissions">
          <Button variant="secondary">Back to list</Button>
        </Link>
      </div>

      {error ? (
        <Card>
          <p className="text-sm text-error m-0">{error}</p>
        </Card>
      ) : null}

      {loading ? (
        <Card>
          <p className="text-sm text-contentSecondary text-center m-0 py-4">Loading...</p>
        </Card>
      ) : null}

      {!loading && !error && detail && (
        <div className="flex flex-col gap-3">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <JsonBlock label="Student" data={detail.student} />
            <JsonBlock label="Task (summary)" data={detail.task} />
          </div>
          <JsonBlock label="Submission" data={detail.submission} />
          <JsonBlock label="Mentor reviews" data={detail.mentor_reviews} />
        </div>
      )}
    </DashboardLayout>
  );
}
