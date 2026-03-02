import { apiRequest } from './client'

export type MonthlyStats = {
  month: string
  total_spend: string
  total_income: string
  breakdown: Array<{ category_id: number; category_name: string; type: string; total: string }>
  budget_vs_actual: Array<{
    category_id: number
    category_name: string
    limit_amount: string
    actual_amount: string
  }>
}

export async function getMonthlyStats(month: string) {
  const res = await apiRequest<MonthlyStats>(`/stats/monthly?month=${month}`)
  return res.data
}
