import { useEffect, useMemo, useState } from 'react'

import { getMonthlyStats } from '../api/stats'

function currentMonth(): string {
  return new Date().toISOString().slice(0, 7)
}

export function DashboardPage() {
  const [month, setMonth] = useState(currentMonth())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<Awaited<ReturnType<typeof getMonthlyStats>> | null>(null)

  useEffect(() => {
    void (async () => {
      try {
        setLoading(true)
        setError(null)
        setStats(await getMonthlyStats(month))
      } catch (err) {
        setError((err as Error).message)
      } finally {
        setLoading(false)
      }
    })()
  }, [month])

  const maxBar = useMemo(() => {
    if (!stats?.breakdown.length) return 1
    return Math.max(...stats.breakdown.map((item) => Number(item.total)), 1)
  }, [stats])

  return (
    <section>
      <div className="page-header">
        <h2>Dashboard</h2>
        <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} />
      </div>
      {loading ? <p>Loading...</p> : null}
      {error ? <p className="error">{error}</p> : null}
      {stats ? (
        <>
          <div className="kpi-grid">
            <article>
              <h3>Total Spend</h3>
              <p>{stats.total_spend}</p>
            </article>
            <article>
              <h3>Total Income</h3>
              <p>{stats.total_income}</p>
            </article>
          </div>
          <h3>Breakdown</h3>
          <div className="bars">
            {stats.breakdown.map((item) => (
              <div key={item.category_id} className="bar-row">
                <span>{item.category_name}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${(Number(item.total) / maxBar) * 100}%` }} />
                </div>
                <b>{item.total}</b>
              </div>
            ))}
          </div>
        </>
      ) : null}
    </section>
  )
}
