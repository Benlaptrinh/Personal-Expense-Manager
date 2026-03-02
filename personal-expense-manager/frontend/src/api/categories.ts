import { apiRequest } from './client'

export type Category = {
  id: number
  name: string
  type: 'income' | 'expense'
  created_at: string
}

export async function getCategories() {
  const res = await apiRequest<Category[]>('/categories')
  return res.data
}

export async function createCategory(payload: { name: string; type: 'income' | 'expense' }) {
  const res = await apiRequest<Category>('/categories', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return res.data
}

export async function deleteCategory(categoryId: number) {
  await apiRequest(`/categories/${categoryId}`, {
    method: 'DELETE',
  })
}
