const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export type ApiResponse<T> = {
  success: boolean
  data: T
  meta?: Record<string, unknown>
  error?: { code: string; message: string; details?: unknown }
}

type Tokens = {
  accessToken: string | null
  refreshToken: string | null
}

let tokens: Tokens = {
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
}

export function setTokens(next: Tokens): void {
  tokens = next
  if (next.accessToken) {
    localStorage.setItem('access_token', next.accessToken)
  } else {
    localStorage.removeItem('access_token')
  }

  if (next.refreshToken) {
    localStorage.setItem('refresh_token', next.refreshToken)
  } else {
    localStorage.removeItem('refresh_token')
  }
}

async function refreshAccessToken(): Promise<boolean> {
  if (!tokens.refreshToken) {
    return false
  }

  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: tokens.refreshToken }),
  })

  if (!res.ok) {
    setTokens({ accessToken: null, refreshToken: null })
    return false
  }

  const json = (await res.json()) as ApiResponse<{
    access_token: string
    refresh_token: string
  }>

  setTokens({ accessToken: json.data.access_token, refreshToken: json.data.refresh_token })
  return true
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
  retry = true,
): Promise<ApiResponse<T>> {
  const headers = new Headers(init.headers)
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json')
  }

  if (tokens.accessToken) {
    headers.set('Authorization', `Bearer ${tokens.accessToken}`)
  }

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers })

  if (res.status === 401 && retry && !path.startsWith('/auth/')) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      return apiRequest<T>(path, init, false)
    }
  }

  const json = (await res.json()) as ApiResponse<T>
  if (!res.ok || !json.success) {
    throw new Error(json.error?.message ?? 'API request failed')
  }

  return json
}

export function getApiBase(): string {
  return API_BASE
}
