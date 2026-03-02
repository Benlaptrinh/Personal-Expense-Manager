import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

export function RegisterPage() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    try {
      await register(email, password)
      setMessage('Register success. You can login now.')
      setTimeout(() => navigate('/login'), 800)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <section className="auth-card">
      <h2>Register</h2>
      <form onSubmit={onSubmit}>
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Create account</button>
      </form>
      {message ? <p className="ok">{message}</p> : null}
      {error ? <p className="error">{error}</p> : null}
      <p>
        Have account? <Link to="/login">Login</Link>
      </p>
    </section>
  )
}
