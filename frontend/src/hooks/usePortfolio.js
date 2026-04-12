import { useState, useEffect, useCallback } from 'react'
import { portfolioApi } from '../api/client'
import { getApiErrorMessage } from '../utils/apiError'

export function usePortfolio() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setError('')
    setLoading(true)
    try {
      const res = await portfolioApi.getMe()
      setData(res.data ?? null)
    } catch (err) {
      setData(null)
      setError(getApiErrorMessage(err, 'Could not load portfolio'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { data, loading, error, reload: load }
}
