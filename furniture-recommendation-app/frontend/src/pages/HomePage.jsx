import React from 'react'
import { Link } from 'react-router-dom'
import { MessageSquare, BarChart3, Brain, Zap } from 'lucide-react'

function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            AI-Powered Furniture 
            <span className="text-blue-600"> Recommendations</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Discover perfect furniture for your space through intelligent conversations. 
            Our AI combines machine learning, natural language processing, and computer vision 
            to understand your needs and recommend the ideal pieces.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/chat"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <MessageSquare className="w-5 h-5" />
              Start Chatting
            </Link>
            <Link
              to="/analytics"
              className="border border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors flex items-center gap-2"
            >
              <BarChart3 className="w-5 h-5" />
              View Analytics
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Brain className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Smart Recommendations</h3>
            <p className="text-gray-600">AI-powered suggestions based on your style, space, and preferences</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm">
            <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <MessageSquare className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Natural Conversation</h3>
            <p className="text-gray-600">Chat naturally about what you need - no complex forms or filters</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm">
            <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Market Insights</h3>
            <p className="text-gray-600">Comprehensive analytics and trends in furniture preferences</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm">
            <div className="bg-orange-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-orange-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Instant Results</h3>
            <p className="text-gray-600">Get personalized recommendations in seconds, not hours</p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-2xl p-8 mb-16 shadow-sm">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">1</div>
              <h3 className="text-lg font-semibold mb-2">Describe Your Needs</h3>
              <p className="text-gray-600">Tell us about your space, style preferences, and what you're looking for</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">2</div>
              <h3 className="text-lg font-semibold mb-2">AI Analysis</h3>
              <p className="text-gray-600">Our AI processes your requirements using advanced ML algorithms</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">3</div>
              <h3 className="text-lg font-semibold mb-2">Get Recommendations</h3>
              <p className="text-gray-600">Receive personalized furniture suggestions with detailed explanations</p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-8">Powered by Advanced AI</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">4+</div>
              <div className="text-gray-600">AI Domains</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">10K+</div>
              <div className="text-gray-600">Product Catalog</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">90%+</div>
              <div className="text-gray-600">Accuracy Rate</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">&lt;1s</div>
              <div className="text-gray-600">Response Time</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage