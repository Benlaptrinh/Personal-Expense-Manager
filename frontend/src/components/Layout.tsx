import { Link, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/expenses', label: 'Expenses' },
  { to: '/categories', label: 'Categories' },
  { to: '/budgets', label: 'Budgets' },
]

export function Layout() {
  const location = useLocation()
  const { logout, role } = useAuth()

  return (
    <div className="shell">
      <aside className="sidebar">
        <h1>Expense Manager</h1>
        <p className="muted">Role: {role ?? 'user'}</p>
        <nav>
          {links.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={location.pathname === item.to ? 'active' : ''}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <button onClick={() => logout()} className="danger">Logout</button>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
