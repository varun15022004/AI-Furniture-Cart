import React, { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Package, DollarSign, Users, ShoppingCart, Star, Globe } from 'lucide-react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      setIsLoading(true)
      const response = await axios.get(`${API_BASE_URL}/analytics`)
      setAnalytics(response.data)
      setError(null)
    } catch (error) {
      console.error('Error fetching analytics:', error)
      // Fallback demo data with enhanced metrics
      setAnalytics({
        totalProducts: 1247,
        totalCategories: 18,
        averagePrice: 289.99,
        totalBrands: 45,
        categoryDistribution: {
          'Living Room': 324,
          'Bedroom': 287,
          'Office': 198,
          'Dining Room': 156,
          'Kitchen': 134,
          'Bathroom': 98,
          'Outdoor': 50
        },
        priceStatistics: {
          mean: 289.99,
          median: 199.99,
          min: 19.99,
          max: 2499.99,
          std: 245.67
        },
        brandDistribution: {
          'IKEA': 89,
          'West Elm': 76,
          'Pottery Barn': 64,
          'Herman Miller': 45,
          'CB2': 38,
          'Others': 935
        },
        materialDistribution: {
          'Wood': 456,
          'Metal': 287,
          'Fabric': 234,
          'Leather': 145,
          'Glass': 89,
          'Plastic': 36
        },
        countryDistribution: {
          'USA': 567,
          'China': 234,
          'Italy': 123,
          'Germany': 98,
          'Sweden': 87,
          'Others': 138
        },
        priceRanges: [
          { range: '$0-50', count: 198, percentage: 16 },
          { range: '$51-100', count: 287, percentage: 23 },
          { range: '$101-250', count: 324, percentage: 26 },
          { range: '$251-500', count: 234, percentage: 19 },
          { range: '$501-1000', count: 156, percentage: 12 },
          { range: '$1000+', count: 48, percentage: 4 }
        ],
        popularSearches: [
          'office chair', 'dining table', 'sofa', 'desk', 'bookshelf',
          'coffee table', 'bed frame', 'nightstand', 'dresser', 'lamp'
        ]
      })
      setError('Using demo data - API connection unavailable')
    } finally {
      setIsLoading(false)
    }
  }

  const KPICard = ({ icon: Icon, title, value, subtitle, gradient, change }) => (
    <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 hover:bg-slate-800/80 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <div className={`p-3 rounded-lg ${gradient}`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-slate-300 font-medium text-sm">{title}</h3>
          </div>
          <div className="space-y-1">
            <p className="text-3xl font-bold text-slate-100">{value}</p>
            <p className="text-slate-400 text-sm">{subtitle}</p>
            {change && (
              <div className="flex items-center gap-1 text-xs">
                <TrendingUp className="w-3 h-3 text-green-400" />
                <span className="text-green-400 font-medium">{change}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )

  const ChartCard = ({ title, children, description }) => (
    <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6 hover:bg-slate-800/80 transition-all duration-300">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-slate-100 mb-2">{title}</h3>
        {description && <p className="text-slate-400 text-sm">{description}</p>}
      </div>
      {children}
    </div>
  )

  const ProgressBar = ({ label, value, maxValue, color = "blue" }) => {
    const percentage = (value / maxValue) * 100
    const colorClasses = {
      blue: "bg-blue-500",
      purple: "bg-purple-500",
      green: "bg-green-500",
      orange: "bg-orange-500",
      red: "bg-red-500",
      teal: "bg-teal-500"
    }
    
    return (
      <div className="mb-4 last:mb-0">
        <div className="flex justify-between items-center mb-2">
          <span className="text-slate-300 text-sm font-medium">{label}</span>
          <span className="text-slate-400 text-xs">{value} products</span>
        </div>
        <div className="w-full bg-slate-700/50 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${colorClasses[color]} transition-all duration-500 ease-out`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="text-right mt-1">
          <span className="text-slate-500 text-xs">{percentage.toFixed(1)}%</span>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-r-transparent mb-4"></div>
          <p className="text-slate-400">Loading analytics data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Analytics Dashboard
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Comprehensive insights into our product catalog and customer preferences
          </p>
          {error && (
            <div className="bg-orange-500/20 border border-orange-500/50 rounded-lg p-3 max-w-md mx-auto">
              <p className="text-orange-200 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            icon={Package}
            title="Total Products"
            value={analytics?.totalProducts?.toLocaleString() || '0'}
            subtitle="In our catalog"
            gradient="bg-gradient-to-r from-blue-500 to-blue-600"
            change="+12.3% this month"
          />
          <KPICard
            icon={BarChart3}
            title="Categories"
            value={analytics?.totalCategories || '0'}
            subtitle="Product categories"
            gradient="bg-gradient-to-r from-purple-500 to-purple-600"
            change="+2 new categories"
          />
          <KPICard
            icon={DollarSign}
            title="Avg. Price"
            value={`$${analytics?.averagePrice?.toFixed(2) || '0'}`}
            subtitle="Average product price"
            gradient="bg-gradient-to-r from-green-500 to-green-600"
            change="+5.2% vs last quarter"
          />
          <KPICard
            icon={Star}
            title="Brands"
            value={analytics?.totalBrands || '0'}
            subtitle="Unique brands"
            gradient="bg-gradient-to-r from-orange-500 to-orange-600"
            change="+8 new brands"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Category Distribution */}
          <ChartCard 
            title="Products by Category" 
            description="Distribution of products across different categories"
          >
            <div className="space-y-3">
              {Object.entries(analytics?.categoryDistribution || {}).map(([category, count], index) => (
                <ProgressBar
                  key={category}
                  label={category}
                  value={count}
                  maxValue={Math.max(...Object.values(analytics?.categoryDistribution || {}))}
                  color={['blue', 'purple', 'green', 'orange', 'red', 'teal'][index % 6]}
                />
              ))}
            </div>
          </ChartCard>

          {/* Price Range Distribution */}
          <ChartCard 
            title="Price Range Distribution" 
            description="How products are distributed across price ranges"
          >
            <div className="space-y-3">
              {analytics?.priceRanges?.map((range, index) => (
                <ProgressBar
                  key={range.range}
                  label={range.range}
                  value={range.count}
                  maxValue={Math.max(...(analytics?.priceRanges?.map(r => r.count) || []))}
                  color={['green', 'blue', 'purple', 'orange', 'red', 'teal'][index % 6]}
                />
              )) || <div className="text-slate-400">No data available</div>}
            </div>
          </ChartCard>

          {/* Top Brands */}
          <ChartCard 
            title="Top Brands" 
            description="Most popular brands in our catalog"
          >
            <div className="space-y-3">
              {Object.entries(analytics?.brandDistribution || {}).slice(0, 6).map(([brand, count], index) => (
                <ProgressBar
                  key={brand}
                  label={brand}
                  value={count}
                  maxValue={Math.max(...Object.values(analytics?.brandDistribution || {}))}
                  color={['blue', 'purple', 'green', 'orange', 'red', 'teal'][index % 6]}
                />
              ))}
            </div>
          </ChartCard>

          {/* Material Distribution */}
          <ChartCard 
            title="Materials Used" 
            description="Distribution of materials across all products"
          >
            <div className="space-y-3">
              {Object.entries(analytics?.materialDistribution || {}).map(([material, count], index) => (
                <ProgressBar
                  key={material}
                  label={material}
                  value={count}
                  maxValue={Math.max(...Object.values(analytics?.materialDistribution || {}))}
                  color={['green', 'blue', 'purple', 'orange', 'red', 'teal'][index % 6]}
                />
              ))}
            </div>
          </ChartCard>
        </div>

        {/* Additional Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Popular Searches */}
          <ChartCard 
            title="Popular Search Terms" 
            description="Most frequently searched product types"
          >
            <div className="flex flex-wrap gap-2">
              {analytics?.popularSearches?.map((term, index) => (
                <span
                  key={term}
                  className={`px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${
                    ['from-blue-500 to-blue-600', 'from-purple-500 to-purple-600', 'from-green-500 to-green-600', 
                     'from-orange-500 to-orange-600', 'from-red-500 to-red-600', 'from-teal-500 to-teal-600'][index % 6]
                  } text-white`}
                >
                  {term}
                </span>
              )) || <div className="text-slate-400">No data available</div>}
            </div>
          </ChartCard>

          {/* Price Statistics */}
          <ChartCard 
            title="Price Statistics" 
            description="Statistical breakdown of product pricing"
          >
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-700/30 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-1">Minimum Price</p>
                <p className="text-2xl font-bold text-green-400">${analytics?.priceStatistics?.min}</p>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-1">Maximum Price</p>
                <p className="text-2xl font-bold text-red-400">${analytics?.priceStatistics?.max}</p>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-1">Median Price</p>
                <p className="text-2xl font-bold text-blue-400">${analytics?.priceStatistics?.median}</p>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-1">Std Deviation</p>
                <p className="text-2xl font-bold text-purple-400">${analytics?.priceStatistics?.std?.toFixed(2)}</p>
              </div>
            </div>
          </ChartCard>
        </div>

        {/* Country Distribution */}
        <ChartCard 
          title="Products by Country of Origin" 
          description="Geographic distribution of our product catalog"
        >
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(analytics?.countryDistribution || {}).map(([country, count], index) => (
              <div key={country} className="bg-slate-700/30 rounded-lg p-4 text-center hover:bg-slate-700/50 transition-colors">
                <Globe className={`w-8 h-8 mx-auto mb-2 ${
                  ['text-blue-400', 'text-purple-400', 'text-green-400', 'text-orange-400', 'text-red-400', 'text-teal-400'][index % 6]
                }`} />
                <p className="text-slate-300 font-semibold">{country}</p>
                <p className="text-slate-400 text-sm">{count} products</p>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>
    </div>
  )
}

export default AnalyticsPage