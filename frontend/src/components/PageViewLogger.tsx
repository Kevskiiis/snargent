import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { sendLog } from '../api/logging'

export function PageViewLogger() {
  const { pathname } = useLocation()
  const lastLoggedPath = useRef<string | null>(null)

  useEffect(() => {
    if (lastLoggedPath.current === pathname) {
      return
    }
    lastLoggedPath.current = pathname

    void sendLog({
      page: pathname,
      eventType: 'page_view',
      fields: {},
      timestamp: new Date().toISOString(),
    }).catch((error: unknown) => {
      console.error('Unable to log page view:', error)
    })
  }, [pathname])

  return null
}
