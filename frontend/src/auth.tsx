import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import { authService } from './services'
import type { Session } from './types'

const SESSION_KEY = 'dayflow:session'

interface AuthContextValue {
  session: Session | null
  login: (loginId: string, password: string) => Promise<Session>
  setup: (email: string, password: string) => Promise<Session>
  changePassword: (password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function restoreSession(): Session | null {
  try {
    const stored = sessionStorage.getItem(SESSION_KEY)
    return stored ? JSON.parse(stored) as Session : null
  } catch {
    sessionStorage.removeItem(SESSION_KEY)
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(restoreSession)

  const value = useMemo<AuthContextValue>(() => ({
    session,
    login: async (loginId, password) => {
      const next = await authService.login(loginId, password)
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(next))
      setSession(next)
      return next
    },
    setup: async (email, password) => {
      const next = await authService.setup(email, password)
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(next))
      setSession(next)
      return next
    },
    changePassword: async (password) => {
      if (!session) return
      const next = await authService.changePassword(session, password)
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(next))
      setSession(next)
    },
    logout: () => {
      sessionStorage.removeItem(SESSION_KEY)
      setSession(null)
    },
  }), [session])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside AuthProvider')
  return value
}

export function roleLanding(session: Session) {
  return session.role === 'employee' ? '/profile' : '/employees'
}
