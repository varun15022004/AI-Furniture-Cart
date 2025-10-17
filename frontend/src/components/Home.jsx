import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiSearch, FiTrendingUp, FiAward, FiShield, FiArrowRight, FiStar, FiHeart, FiTruck, FiClock } from 'react-icons/fi';

const Home = () => {
  const featuredCategories = [
    {
      name: 'Living Room',
      image: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500&h=300&fit=crop',
      description: 'Comfortable sofas and seating arrangements',
      link: '/shop?category=living'
    },
    {
      name: 'Bedroom',
      image: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&h=300&fit=crop',
      description: 'Cozy beds and bedroom essentials',
      link: '/shop?category=bedroom'
    },
    {
      name: 'Office',
      image: 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=500&h=300&fit=crop',
      description: 'Ergonomic office furniture',
      link: '/shop?category=office'
    },
    {
      name: 'Dining',
      image: 'https://images.unsplash.com/photo-1556912167-f556f1e3b83e?w=500&h=300&fit=crop',
      description: 'Elegant dining sets',
      link: '/shop?category=dining'
    }
  ];

  const features = [
    {
      icon: <FiTruck className="w-8 h-8 text-amber-600" />,
      title: 'Free Shipping',
      description: 'Free delivery on orders over $499'
    },
    {
      icon: <FiShield className="w-8 h-8 text-amber-600" />,
      title: '2-Year Warranty',
      description: 'Comprehensive protection plan'
    },
    {
      icon: <FiAward className="w-8 h-8 text-amber-600" />,
      title: 'Premium Quality',
      description: 'Crafted from the finest materials'
    },
    {
      icon: <FiClock className="w-8 h-8 text-amber-600" />,
      title: 'Quick Delivery',
      description: 'Most items delivered in 3-5 days'
    }
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-amber-50 via-white to-orange-50 py-20 overflow-hidden min-h-screen flex items-center">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-32 w-96 h-96 bg-gradient-to-br from-amber-200/30 to-orange-200/30 rounded-full blur-3xl animate-float"></div>
          <div className="absolute -bottom-40 -left-32 w-96 h-96 bg-gradient-to-br from-yellow-200/30 to-amber-200/30 rounded-full blur-3xl animate-float-delayed"></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left animate-fade-in-up">
              <div className="mb-6">
                <span className="inline-block bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-2 rounded-full text-sm font-semibold mb-4 animate-bounce">
                  ✨ AI-Powered Furniture Store
                </span>
              </div>
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-serif font-bold text-gray-900 mb-8 leading-tight">
                Crafted for{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-600 via-orange-500 to-amber-600 animate-gradient">
                  Comfort
                </span>
                <br className="hidden sm:block" />
                Built for{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-600 via-amber-500 to-orange-600 animate-gradient-reverse">
                  Life
                </span>
              </h1>
              <p className="text-xl lg:text-2xl text-gray-600 mb-10 max-w-2xl leading-relaxed">
                Discover premium furniture pieces curated by AI to match your unique style and transform your space into the home of your dreams.
              </p>
              <div className="flex flex-col sm:flex-row gap-6 justify-center lg:justify-start">
                <Link
                  to="/shop"
                  className="group bg-gradient-to-r from-amber-600 to-orange-600 text-white px-10 py-5 rounded-2xl font-bold text-lg hover:from-amber-700 hover:to-orange-700 transition-all duration-300 text-center shadow-2xl hover:shadow-3xl transform hover:-translate-y-2 hover:scale-105 flex items-center justify-center gap-3"
                >
                  <span>Shop Collection</span>
                  <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  to="/shop?search=modern"
                  className="group border-3 border-amber-500 text-amber-600 px-10 py-5 rounded-2xl font-bold text-lg hover:bg-amber-500 hover:text-white transition-all duration-300 text-center shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center gap-3 backdrop-blur-sm"
                >
                  <FiSearch className="w-5 h-5" />
                  <span>AI Search</span>
                </Link>
              </div>
            </div>
            <div className="relative animate-fade-in-up animation-delay-200">
              <div className="relative z-10 group">
                <img
                  src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop&q=80"
                  alt="Modern Living Room"
                  className="rounded-3xl shadow-3xl w-full h-auto group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              {/* Enhanced decorative elements */}
              <div className="absolute -top-6 -right-6 w-32 h-32 bg-gradient-to-br from-amber-400 to-orange-400 rounded-full opacity-70 animate-pulse blur-sm"></div>
              <div className="absolute -bottom-6 -left-6 w-24 h-24 bg-gradient-to-br from-yellow-400 to-amber-400 rounded-full opacity-70 animate-pulse delay-1000 blur-sm"></div>
              <div className="absolute top-1/2 -right-4 w-16 h-16 bg-gradient-to-br from-orange-300 to-red-300 rounded-full opacity-50 animate-bounce delay-500"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center group">
                <div className="bg-amber-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-amber-100 transition-colors duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Categories */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-serif font-bold text-gray-900 mb-4">Shop by Category</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">Find the perfect pieces for every room in your home</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {featuredCategories.map((category, index) => (
              <Link
                key={index}
                to={category.link}
                className="group relative overflow-hidden rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
              >
                <div className="aspect-w-4 aspect-h-3">
                  <img
                    src={category.image}
                    alt={category.name}
                    className="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-700"
                  />
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent group-hover:from-black/70 transition-all duration-300"></div>
                <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                  <h3 className="text-xl font-semibold mb-2 transform translate-y-0 group-hover:-translate-y-1 transition-transform duration-300">
                    {category.name}
                  </h3>
                  <p className="text-sm opacity-90 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-300">
                    {category.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* AI Recommendation CTA */}
      <section className="py-16 bg-gradient-to-r from-amber-600 via-orange-600 to-yellow-600 text-white relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-white rounded-full"></div>
          <div className="absolute bottom-1/4 right-1/4 w-32 h-32 bg-white rounded-full"></div>
        </div>
        
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8 relative">
          <h2 className="text-4xl font-serif font-bold mb-4">Can't Find What You're Looking For?</h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Let our AI assistant help you discover the perfect furniture pieces for your space with intelligent recommendations.
          </p>
          <Link
            to="/shop"
            className="inline-block bg-white text-amber-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-1 duration-300"
          >
            Try AI Search
          </Link>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="text-4xl font-bold text-amber-600">10K+</div>
              <div className="text-gray-600">Happy Customers</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-amber-600">5K+</div>
              <div className="text-gray-600">Products Available</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-amber-600">98%</div>
              <div className="text-gray-600">Customer Satisfaction</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-amber-600">15+</div>
              <div className="text-gray-600">Years Experience</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;