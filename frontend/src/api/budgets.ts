import { apiRequest } from './client'

export type Budget = {
  id: number
  category_id: number
  category_name: string
  month: string
  limit_amount: string
}

export async function getBudgets(month: string) {
  const res = await apiRequest<Budget[]>(`/budgets?month=${month}`)
  return res.data
}

export async function upsertBudget(categoryId: number, month: string, limitAmount: string) {
  const res = await apiRequest<Budget>(`/budgets/${categoryId}?month=${month}`, {
    method: 'PUT',
    body: JSON.stringify({ limit_amount: limitAmount }),
  })
  return res.data
}
