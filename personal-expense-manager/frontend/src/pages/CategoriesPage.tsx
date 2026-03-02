import { FormEvent, useEffect, useState } from 'react'

import { Category, createCategory, deleteCategory, getCategories } from '../api/categories'

export function CategoriesPage() {
  const [name, setName] = useState('')
  const [type, setType] = useState<'income' | 'expense'>('expense')
  const [categories, setCategories] = useState<Category[]>([])
  const [error, setError] = useState<string | null>(null)

  async function load() {
    try {
      setError(null)
      setCategories(await getCategories())
    } catch (err) {
      setError((err as Error).message)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    await createCategory({ name, type })
    setName('')
    await load()
  }

  return (
    <section>
      <h2>Categories</h2>
      <form onSubmit={onSubmit} className="inline-form">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Category name" />
        <select value={type} onChange={(e) => setType(e.target.value as 'income' | 'expense')}>
          <option value="expense">Expense</option>
          <option value="income">Income</option>
        </select>
        <button type="submit">Add</button>
      </form>
      {error ? <p className="error">{error}</p> : null}
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {categories.map((category) => (
            <tr key={category.id}>
              <td>{category.name}</td>
              <td>{category.type}</td>
              <td>
                <button
                  className="danger"
                  onClick={async () => {
                    await deleteCategory(category.id)
                    await load()
                  }}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
