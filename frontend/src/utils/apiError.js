/**
<<<<<<< HEAD
 * Consistent error messages from Flask/axios (message, detail, status, network).
 */
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
=======
 * Normalize Axios / API errors for user-facing messages.
 * Backend often returns { message: string } or { message, detail }.
 */
export function getApiErrorMessage(error, fallback = 'Something went wrong') {
  if (!error) return fallback
  const data = error.response?.data
  if (data && typeof data.message === 'string' && data.message.trim()) {
    if (typeof data.detail === 'string' && data.detail.trim()) {
      return `${data.message} (${data.detail})`
    }
    return data.message
  }
  if (error.message) return error.message
>>>>>>> origin/master
  return fallback
}
