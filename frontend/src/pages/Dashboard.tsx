import { useState, useEffect } from 'react'
import { DollarSign, TrendingUp, TrendingDown, PiggyBank } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import api from '../utils/api'
import toast from 'react-hot-toast'
import { format, parseISO } from 'date-fns'

interface CategorySummary {
  category_id: number | null
  category_name: string
  category_color: string
  total_amount: number
  transaction_count: number
}

interface Transaction {
  id: number
  amount: number
  description: string
  transaction_type: string
  category_id: number | null
  category_name: string | null
  category_color: string | null
  date: string
  notes: string | null
  ai_categorized: boolean
  created_at: string
}

interface DashboardSummary {
  total_income: number
  total_expenses: number
  net_amount: number
  category_summaries: CategorySummary[]
  recent_transactions: Transaction[]
}

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/api/transactions/summary/dashboard')
      setSummary(response.data)
    } catch (error: any) {
      console.error('Failed to fetch dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    try {
      return format(parseISO(dateString), 'MMM dd')
    } catch {
      return 'Invalid date'
    }
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B6B']

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            Dashboard
          </h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-neutral-200 dark:bg-neutral-700 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-neutral-200 dark:bg-neutral-700 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!summary) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            Dashboard
          </h1>
        </div>
        <div className="card">
          <p className="text-center text-neutral-600 dark:text-neutral-400">
            No data available. Add some transactions to see your dashboard.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
          Dashboard
        </h1>
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          Welcome back! Here's your financial overview.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                Total Income
              </p>
              <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                {formatCurrency(summary.total_income)}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
              <TrendingDown className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                Total Expenses
              </p>
              <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                {formatCurrency(summary.total_expenses)}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
              <DollarSign className="h-6 w-6 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                Net Amount
              </p>
              <p className={`text-2xl font-bold ${summary.net_amount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {formatCurrency(summary.net_amount)}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-secondary-100 dark:bg-secondary-900 rounded-lg">
              <PiggyBank className="h-6 w-6 text-secondary-600 dark:text-secondary-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                Transactions
              </p>
              <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                {summary.recent_transactions.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            Spending by Category
          </h3>
          {summary.category_summaries.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={summary.category_summaries}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ category_name, percent }) => `${category_name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="total_amount"
                >
                  {summary.category_summaries.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.category_color || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-neutral-500 dark:text-neutral-400">
              <p>No spending data available</p>
            </div>
          )}
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            Category Breakdown
          </h3>
          {summary.category_summaries.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={summary.category_summaries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category_name" />
                <YAxis />
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                <Bar dataKey="total_amount" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-neutral-500 dark:text-neutral-400">
              <p>No category data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
          Recent Transactions
        </h3>
        {summary.recent_transactions.length > 0 ? (
          <div className="space-y-4">
            {summary.recent_transactions.map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div>
                  <p className="font-medium text-neutral-900 dark:text-neutral-100">
                    {transaction.description}
                  </p>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    {transaction.category_name || 'Uncategorized'} • {formatDate(transaction.date)}
                  </p>
                </div>
                <span className={`font-medium ${transaction.transaction_type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {transaction.transaction_type === 'income' ? '+' : '-'}{formatCurrency(transaction.amount)}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-neutral-500 dark:text-neutral-400 py-8">
            <p>No transactions yet. Add your first transaction to get started!</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard 