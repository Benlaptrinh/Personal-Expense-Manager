import { createContext, useContext, useMemo, useState } from 'react'

import { login as loginApi, logout as logoutApi, register as registerApi } from '../api/auth'

type AuthContextValue = {
  accessToken: string | null
  refreshToken: string | null
  role: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

function parseRoleFromToken(token: string | null): string | null {
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1])) as { role?: string }
    return payload.role ?? null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(localStorage.getItem('access_token'))
  const [refreshToken, setRefreshToken] = useState<string | null>(localStorage.getItem('refresh_token'))
  const [role, setRole] = useState<string | null>(parseRoleFromToken(localStorage.getItem('access_token')))

  const value = useMemo<AuthContextValue>(
    () => ({
      accessToken,
      refreshToken,
      role,
      isAuthenticated: Boolean(accessToken),
      async login(email: string, password: string) {
        const data = await loginApi({ email, password })
        setAccessToken(data.access_token)
        setRefreshToken(data.refresh_token)
        setRole(parseRoleFromToken(data.access_token))
      },
      async register(email: string, password: string) {
        await registerApi({ email, password })
      },
      async logout() {
        await logoutApi(refreshToken)
        setAccessToken(null)
        setRefreshToken(null)
        setRole(null)
      },
    }),
    [accessToken, refreshToken, role],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return ctx
}
