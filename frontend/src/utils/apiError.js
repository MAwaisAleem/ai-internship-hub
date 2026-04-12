export function getApiErrorMessage(err, fallback = 'Something went wrong') {
  if (!err) return fallback
  const status = err.response?.status
  if (status === 413) {
    return 'Upload is too large. Use a smaller file or check the task size limit.'
  }
  if (status === 403) {
    return err.response?.data?.message || 'You do not have permission for this action.'
  }
  const data = err.response?.data
  if (data && typeof data === 'object') {
    if (typeof data.message === 'string' && data.message) return data.message
    if (typeof data.detail === 'string' && data.detail) return data.detail
  }
  if (!err.response && err.message) return err.message
  return fallback
}
