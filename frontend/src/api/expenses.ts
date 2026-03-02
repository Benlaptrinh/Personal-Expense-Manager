import { apiRequest } from './client'

export type Expense = {
  id: number
  category_id: number
  category_name: string
  amount: string
  currency: string
  note: string | null
  spent_at: string
  created_at: string
}

export async function getExpenses(params: URLSearchParams) {
  const res = await apiRequest<Expense[]>(`/expenses?${params.toString()}`)
  return { items: res.data, meta: res.meta }
}

export async function createExpense(payload: {
  category_id: number
  amount: string
  currency: string
  note?: string
  spent_at: string
}) {
  const res = await apiRequest<Expense>('/expenses', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return res.data
}

export async function deleteExpense(expenseId: number) {
  await apiRequest(`/expenses/${expenseId}`, {
    method: 'DELETE',
  })
}
