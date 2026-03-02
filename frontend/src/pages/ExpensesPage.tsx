import { FormEvent, useEffect, useState } from 'react'

import { Category, getCategories } from '../api/categories'
import { createExpense, deleteExpense, Expense, getExpenses } from '../api/expenses'

function nowIsoDateTime(): string {
  return new Date().toISOString().slice(0, 16)
}

export function ExpensesPage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [page, setPage] = useState(1)
  const [size] = useState(20)
  const [total, setTotal] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const [categoryId, setCategoryId] = useState<number | ''>('')
  const [amount, setAmount] = useState('')
  const [note, setNote] = useState('')
  const [spentAt, setSpentAt] = useState(nowIsoDateTime())
  const [query, setQuery] = useState('')

  async function loadCategories() {
    setCategories(await getCategories())
  }

  async function loadExpenses() {
    const params = new URLSearchParams({ page: String(page), size: String(size) })
    if (query) params.set('q', query)
    const res = await getExpenses(params)
    setExpenses(res.items)
    setTotal(Number(res.meta?.total ?? 0))
  }

  useEffect(() => {
    void (async () => {
      try {
        setError(null)
        await loadCategories()
        await loadExpenses()
      } catch (err) {
        setError((err as Error).message)
      }
    })()
  }, [page])

  async function onCreate(event: FormEvent) {
    event.preventDefault()
    if (!categoryId) return
    await createExpense({
      category_id: Number(categoryId),
      amount,
      currency: 'USD',
      note,
      spent_at: new Date(spentAt).toISOString(),
    })
    setAmount('')
    setNote('')
    await loadExpenses()
  }

  return (
    <section>
      <div className="page-header">
        <h2>Expenses</h2>
        <div className="filters">
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search note/category" />
          <button onClick={() => loadExpenses()}>Apply</button>
        </div>
      </div>

      <form onSubmit={onCreate} className="grid-form">
        <select value={categoryId} onChange={(e) => setCategoryId(Number(e.target.value) || '')}>
          <option value="">Select category</option>
          {categories
            .filter((item) => item.type === 'expense')
            .map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
        </select>
        <input value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="Amount" />
        <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Note" />
        <input type="datetime-local" value={spentAt} onChange={(e) => setSpentAt(e.target.value)} />
        <button type="submit">Add expense</button>
      </form>

      {error ? <p className="error">{error}</p> : null}

      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Note</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td>{new Date(expense.spent_at).toLocaleString()}</td>
              <td>{expense.category_name}</td>
              <td>{expense.amount}</td>
              <td>{expense.note}</td>
              <td>
                <button
                  className="danger"
                  onClick={async () => {
                    await deleteExpense(expense.id)
                    await loadExpenses()
                  }}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="pager">
        <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
          Prev
        </button>
        <span>
          Page {page} / {Math.max(Math.ceil(total / size), 1)}
        </span>
        <button disabled={page >= Math.ceil(total / size)} onClick={() => setPage((p) => p + 1)}>
          Next
        </button>
      </div>
    </section>
  )
}
