/**
 * Read-only preview of submission payload for mentor review (writing / programming / design).
 */
export default function SubmissionBodyPreview({ submission }) {
  const tt = (submission?.task_type || '').toLowerCase()
  if (tt === 'writing' && submission.text_content) {
    return (
      <pre className="text-sm text-content whitespace-pre-wrap font-sans bg-primary p-3 rounded-md border border-borderLight max-h-64 overflow-auto m-0">
        {submission.text_content}
      </pre>
    )
  }
  if (tt === 'programming' && submission.code_content) {
    return (
      <pre className="text-xs font-mono text-content bg-primary p-3 rounded-md border border-borderLight max-h-64 overflow-auto m-0">
        {submission.code_content}
      </pre>
    )
  }
  if (tt === 'design' && submission.design_file) {
    const df = submission.design_file
    return (
      <ul className="text-sm text-content m-0 pl-4">
        <li>File: {df.original_filename || '—'}</li>
        <li>Size: {df.size_bytes != null ? `${df.size_bytes} bytes` : '—'}</li>
        <li>Type: {df.content_type || '—'}</li>
      </ul>
    )
  }
  return <p className="text-sm text-contentSecondary m-0">No raw body available for this type.</p>
}
