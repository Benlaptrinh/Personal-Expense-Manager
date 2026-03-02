import { FormEvent, useEffect, useState } from 'react'

import { getCategories } from '../api/categories'
import { Budget, getBudgets, upsertBudget } from '../api/budgets'

function currentMonth(): string {
  return new Date().toISOString().slice(0, 7)
}

export function BudgetsPage() {
  const [month, setMonth] = useState(currentMonth())
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [categories, setCategories] = useState<Array<{ id: number; name: string; type: string }>>([])
  const [categoryId, setCategoryId] = useState<number | ''>('')
  const [limit, setLimit] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function load() {
    try {
      setError(null)
      const [categoryItems, budgetItems] = await Promise.all([getCategories(), getBudgets(month)])
      setCategories(categoryItems)
      setBudgets(budgetItems)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  useEffect(() => {
    void load()
  }, [month])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!categoryId) return
    await upsertBudget(Number(categoryId), month, limit)
    setLimit('')
    await load()
  }

  return (
    <section>
      <div className="page-header">
        <h2>Budgets</h2>
        <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} />
      </div>

      <form onSubmit={onSubmit} className="inline-form">
        <select value={categoryId} onChange={(e) => setCategoryId(Number(e.target.value) || '')}>
          <option value="">Select expense category</option>
          {categories
            .filter((item) => item.type === 'expense')
            .map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
        </select>
        <input placeholder="Limit amount" value={limit} onChange={(e) => setLimit(e.target.value)} />
        <button type="submit">Save budget</button>
      </form>

      {error ? <p className="error">{error}</p> : null}

      <table>
        <thead>
          <tr>
            <th>Category</th>
            <th>Month</th>
            <th>Limit</th>
          </tr>
        </thead>
        <tbody>
          {budgets.map((item) => (
            <tr key={item.id}>
              <td>{item.category_name}</td>
              <td>{item.month}</td>
              <td>{item.limit_amount}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
