import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <section className="auth-card">
      <h2>Login</h2>
      <form onSubmit={onSubmit}>
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Login</button>
      </form>
      {error ? <p className="error">{error}</p> : null}
      <p>
        Need account? <Link to="/register">Register</Link>
      </p>
    </section>
  )
}
