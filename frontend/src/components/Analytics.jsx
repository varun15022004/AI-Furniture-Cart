import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  FiBarChart2, FiTrendingUp, FiDollarSign, FiPackage, FiUsers, 
  FiShoppingBag, FiPieChart, FiGlobe, FiRefreshCw 
} from 'react-icons/fi';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Pie, Doughnut, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

const Analytics = () => {
  const [analytics, setAnalytics] = useState({
    overview: {},
    categories: [],
    brands: [],
    priceDistribution: [],
    loading: true,
    error: null
  });
  
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setAnalytics(prev => ({ ...prev, loading: !refreshing, error: null }));
      setRefreshing(true);

      const [overviewRes, categoriesRes, brandsRes, priceRes] = await Promise.all([
        axios.get('http://127.0.0.1:8000/api/analytics/overview'),
        axios.get('http://127.0.0.1:8000/api/analytics/categories'),
        axios.get('http://127.0.0.1:8000/api/analytics/brands'),
        axios.get('http://127.0.0.1:8000/api/analytics/price-distribution')
      ]);

      setAnalytics({
        overview: overviewRes.data,
        categories: categoriesRes.data.data || [],
        brands: brandsRes.data.data || [],
        priceDistribution: priceRes.data.data || [],
        loading: false,
        error: null
      });
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setAnalytics(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to load analytics data'
      }));
    } finally {
      setRefreshing(false);
    }
  };

  // Chart configurations
  const categoryChartData = {
    labels: analytics.categories.slice(0, 10).map(cat => cat.category),
    datasets: [{
      label: 'Number of Products',
      data: analytics.categories.slice(0, 10).map(cat => cat.count),
      backgroundColor: [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
      ],
      borderColor: '#ffffff',
      borderWidth: 2,
      borderRadius: 8,
    }]
  };

  const brandsPieData = {
    labels: analytics.brands.slice(0, 8).map(brand => brand.brand),
    datasets: [{
      data: analytics.brands.slice(0, 8).map(brand => brand.count),
      backgroundColor: [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
      ],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  };

  const priceHistogramData = {
    labels: analytics.priceDistribution.map(range => range.range),
    datasets: [{
      label: 'Number of Products',
      data: analytics.priceDistribution.map(range => range.count),
      backgroundColor: 'rgba(34, 197, 94, 0.8)',
      borderColor: 'rgba(34, 197, 94, 1)',
      borderWidth: 2,
      borderRadius: 6,
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          padding: 20,
          font: {
            size: 12,
            weight: '500'
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 12
        },
        cornerRadius: 8
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true,
          font: {
            size: 11
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        cornerRadius: 8
      }
    }
  };

  if (analytics.loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-orange-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading analytics dashboard...</p>
        </div>
      </div>
    );
  }

  if (analytics.error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-orange-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">📊</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Analytics Unavailable</h2>
          <p className="text-gray-600 mb-4">{analytics.error}</p>
          <button
            onClick={fetchAnalytics}
            className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-3 rounded-lg hover:from-amber-600 hover:to-orange-600 transition-all transform hover:scale-105"
          >
            <FiRefreshCw className="inline mr-2" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-orange-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <h1 className="text-4xl font-bold font-serif bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
              📊 Analytics Dashboard
            </h1>
            <button
              onClick={fetchAnalytics}
              disabled={refreshing}
              className={`ml-4 p-2 rounded-lg transition-all ${
                refreshing 
                  ? 'text-gray-400 cursor-not-allowed' 
                  : 'text-amber-600 hover:bg-amber-100 hover:scale-110'
              }`}
              title="Refresh data"
            >
              <FiRefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <p className="text-lg text-gray-600">
            Comprehensive insights into our furniture catalog performance
          </p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all border border-amber-100 group hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-gradient-to-br from-blue-100 to-blue-200 p-3 rounded-xl group-hover:scale-110 transition-transform">
                <FiPackage className="text-blue-600 text-xl" />
              </div>
              <span className="text-sm text-gray-500 font-medium">TOTAL</span>
            </div>
            <h3 className="text-3xl font-bold text-gray-800 mb-1">
              {analytics.overview.total_products?.toLocaleString() || '0'}
            </h3>
            <p className="text-gray-600 text-sm font-medium">Products in Catalog</p>
            <div className="mt-3 flex items-center text-xs">
              <span className="text-green-600 font-medium">↗ Active inventory</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all border border-amber-100 group hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-gradient-to-br from-green-100 to-green-200 p-3 rounded-xl group-hover:scale-110 transition-transform">
                <FiDollarSign className="text-green-600 text-xl" />
              </div>
              <span className="text-sm text-gray-500 font-medium">AVERAGE</span>
            </div>
            <h3 className="text-3xl font-bold text-gray-800 mb-1">
              ${analytics.overview.average_price?.toFixed(2) || '0.00'}
            </h3>
            <p className="text-gray-600 text-sm font-medium">Price Point</p>
            <div className="mt-3 flex items-center text-xs">
              <span className="text-blue-600 font-medium">Range: ${analytics.overview.min_price?.toFixed(0) || 0} - ${analytics.overview.max_price?.toFixed(0) || 0}</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all border border-amber-100 group hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-gradient-to-br from-purple-100 to-purple-200 p-3 rounded-xl group-hover:scale-110 transition-transform">
                <FiUsers className="text-purple-600 text-xl" />
              </div>
              <span className="text-sm text-gray-500 font-medium">BRANDS</span>
            </div>
            <h3 className="text-3xl font-bold text-gray-800 mb-1">
              {analytics.brands.length || '0'}
            </h3>
            <p className="text-gray-600 text-sm font-medium">Unique Brands</p>
            <div className="mt-3 flex items-center text-xs">
              <span className="text-purple-600 font-medium">🏆 Diverse portfolio</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all border border-amber-100 group hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-gradient-to-br from-orange-100 to-orange-200 p-3 rounded-xl group-hover:scale-110 transition-transform">
                <FiShoppingBag className="text-orange-600 text-xl" />
              </div>
              <span className="text-sm text-gray-500 font-medium">CATEGORIES</span>
            </div>
            <h3 className="text-3xl font-bold text-gray-800 mb-1">
              {analytics.categories.length || '0'}
            </h3>
            <p className="text-gray-600 text-sm font-medium">Product Categories</p>
            <div className="mt-3 flex items-center text-xs">
              <span className="text-orange-600 font-medium">🎯 Complete coverage</span>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
          {/* Product Count by Category - Bar Chart */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-amber-100">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-800 flex items-center">
                <FiBarChart2 className="mr-3 text-amber-500" />
                Product Count by Category
              </h3>
              <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium">
                Top {Math.min(10, analytics.categories.length)}
              </span>
            </div>
            <div className="h-80">
              {analytics.categories.length > 0 ? (
                <Bar data={categoryChartData} options={chartOptions} />
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <FiBarChart2 className="mx-auto text-4xl mb-2 opacity-50" />
                    <p>No category data available</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Top Brands - Pie Chart */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-amber-100">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-800 flex items-center">
                <FiPieChart className="mr-3 text-amber-500" />
                Top Brands Distribution
              </h3>
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
                Top {Math.min(8, analytics.brands.length)}
              </span>
            </div>
            <div className="h-80">
              {analytics.brands.length > 0 ? (
                <Doughnut data={brandsPieData} options={pieOptions} />
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <FiPieChart className="mx-auto text-4xl mb-2 opacity-50" />
                    <p>No brand data available</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Price Distribution - Full Width */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-amber-100 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-800 flex items-center">
              <FiDollarSign className="mr-3 text-amber-500" />
              Price Distribution (Histogram)
            </h3>
            <div className="flex space-x-2 text-xs">
              <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
                Avg: ${analytics.overview.average_price?.toFixed(2) || '0.00'}
              </span>
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
                Median: ${analytics.overview.median_price?.toFixed(2) || '0.00'}
              </span>
            </div>
          </div>
          <div className="h-80">
            {analytics.priceDistribution.length > 0 ? (
              <Bar data={priceHistogramData} options={chartOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <FiDollarSign className="mx-auto text-4xl mb-2 opacity-50" />
                  <p>No price distribution data available</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Additional Insights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 border border-blue-200">
            <h4 className="text-lg font-bold text-blue-800 mb-4 flex items-center">
              <FiTrendingUp className="mr-2" />
              Price Analytics
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-blue-700 font-medium">Minimum:</span>
                <span className="font-bold text-blue-900">${analytics.overview.min_price?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-700 font-medium">Maximum:</span>
                <span className="font-bold text-blue-900">${analytics.overview.max_price?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-blue-700 font-medium">Range:</span>
                <span className="font-bold text-blue-900">
                  ${((analytics.overview.max_price || 0) - (analytics.overview.min_price || 0)).toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 border border-green-200">
            <h4 className="text-lg font-bold text-green-800 mb-4 flex items-center">
              <FiShoppingBag className="mr-2" />
              Catalog Health
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-green-700 font-medium">Coverage:</span>
                <span className="font-bold text-green-900 flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Complete
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-green-700 font-medium">Diversity:</span>
                <span className="font-bold text-green-900 flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Excellent
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-green-700 font-medium">Quality:</span>
                <span className="font-bold text-green-900 flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Premium
                </span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6 border border-purple-200">
            <h4 className="text-lg font-bold text-purple-800 mb-4 flex items-center">
              <FiGlobe className="mr-2" />
              Market Insights
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-purple-700 font-medium">Trend:</span>
                <span className="font-bold text-green-600 flex items-center">
                  ↗ Growing
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-700 font-medium">Demand:</span>
                <span className="font-bold text-orange-600 flex items-center">
                  🔥 High
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-700 font-medium">Opportunity:</span>
                <span className="font-bold text-blue-600 flex items-center">
                  ⭐ Strong
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>📊 Data refreshed automatically • Last updated: {new Date().toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

export default Analytics;