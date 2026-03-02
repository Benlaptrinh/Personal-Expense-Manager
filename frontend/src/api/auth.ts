import { apiRequest, setTokens } from './client'

export async function register(payload: { email: string; password: string }): Promise<void> {
  await apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function login(payload: { email: string; password: string }) {
  const res = await apiRequest<{ access_token: string; refresh_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  setTokens({ accessToken: res.data.access_token, refreshToken: res.data.refresh_token })
  return res.data
}

export async function logout(refreshToken: string | null): Promise<void> {
  if (refreshToken) {
    await apiRequest('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
  }
  setTokens({ accessToken: null, refreshToken: null })
}
