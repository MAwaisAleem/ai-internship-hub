/**
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
  return fallback
}
