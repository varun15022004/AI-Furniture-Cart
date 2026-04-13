import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import axios from 'axios';
import ProductCard from './UI/ProductCard';
import FilterSidebar from './UI/FilterSidebar';
import SearchBar from './UI/SearchBar';
import LoadingSpinner from './UI/LoadingSpinner';

const Shop = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    priceRange: [0, 10000],
    material: '',
    brand: ''
  });
  const [sortBy, setSortBy] = useState('relevance');
  const [error, setError] = useState('');

  const location = useLocation();

  useEffect(() => {
    // Extract parameters from URL
    const urlParams = new URLSearchParams(location.search);
    const searchParam = urlParams.get('search');
    const categoryParam = urlParams.get('category');

    if (searchParam) {
      setSearchQuery(searchParam);
      handleSearch(searchParam);
    } else if (categoryParam) {
      setFilters(prev => ({ ...prev, category: categoryParam }));
      fetchProducts();
    } else {
      fetchProducts();
    }
  }, [location]);

  const fetchProducts = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('/api/products', {
        params: {
          limit: 50
        }
      });
      setProducts(response.data.data || []);
      setFilteredProducts(response.data.data || []);
    } catch (error) {
      console.error('Error fetching products:', error);
      setError('Failed to load products. Please try again.');
      setProducts([]);
      setFilteredProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('/api/products/search', {
        params: {
          q: query,
          limit: 50
        }
      });
      setProducts(response.data.data || []);
      setFilteredProducts(response.data.data || []);
    } catch (error) {
      console.error('Search error:', error);
      setError('Search failed. Please try again.');
      // Fallback to regular products if search fails
      fetchProducts();
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...products];

    // Category filter
    if (filters.category) {
      filtered = filtered.filter(product => {
        const categories = product.categories || product.categories_clean || '';
        return String(categories).toLowerCase().includes(filters.category.toLowerCase());
      });
    }

    // Price range filter
    filtered = filtered.filter(product => {
      const price = parseFloat(product.price_num) || 0;
      return price >= filters.priceRange[0] && price <= filters.priceRange[1];
    });

    // Material filter
    if (filters.material) {
      filtered = filtered.filter(product => {
        const material = product.material || product.material_norm || '';
        return String(material).toLowerCase().includes(filters.material.toLowerCase());
      });
    }

    // Brand filter
    if (filters.brand) {
      filtered = filtered.filter(product => {
        const brand = product.brand || product.brand_norm || '';
        return String(brand).toLowerCase().includes(filters.brand.toLowerCase());
      });
    }

    // Sort products
    switch (sortBy) {
      case 'price-low':
        filtered.sort((a, b) => (parseFloat(a.price_num) || 0) - (parseFloat(b.price_num) || 0));
        break;
      case 'price-high':
        filtered.sort((a, b) => (parseFloat(b.price_num) || 0) - (parseFloat(a.price_num) || 0));
        break;
      case 'name':
        filtered.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
        break;
      case 'relevance':
      default:
        // Keep original order for search results, or sort by similarity_score if available
        if (searchQuery) {
          filtered.sort((a, b) => (b.similarity_score || 0) - (a.similarity_score || 0));
        }
        break;
    }

    setFilteredProducts(filtered);
  };

  useEffect(() => {
    applyFilters();
  }, [filters, sortBy, products]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-orange-50">
      {/* Shop Header */}
      <div className="bg-gradient-to-r from-amber-600 via-orange-500 to-amber-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-serif font-bold mb-4">
            Premium Furniture Collection
          </h1>
          <p className="text-xl opacity-90 max-w-2xl mx-auto">
            Discover handpicked pieces designed to transform your space
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 text-red-700 px-6 py-4 rounded-lg mb-6 shadow-sm animate-fade-in-up">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <div className="lg:w-1/4">
            <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-8">
              <FilterSidebar filters={filters} setFilters={setFilters} />
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:w-3/4">
            {/* Search and Sort Header */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-8">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="flex-1 max-w-md">
                  <SearchBar 
                    searchQuery={searchQuery}
                    setSearchQuery={setSearchQuery}
                    onSearch={handleSearch}
                  />
                </div>
                
                <div className="flex items-center space-x-6">
                  <div className="text-sm text-gray-600 bg-amber-50 px-3 py-2 rounded-full">
                    <span className="font-semibold text-amber-700">
                      {filteredProducts.length}
                    </span>
                    <span className="ml-1">
                      product{filteredProducts.length !== 1 ? 's' : ''}
                      {searchQuery && ` for "${searchQuery}"`}
                    </span>
                  </div>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="border border-gray-300 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none bg-white shadow-sm hover:shadow-md transition-shadow"
                  >
                    <option value="relevance">Sort by Relevance</option>
                    <option value="price-low">Price: Low to High</option>
                    <option value="price-high">Price: High to Low</option>
                    <option value="name">Name A-Z</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Products Grid */}
            {filteredProducts.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                {filteredProducts.map((product, index) => (
                  <div key={product.uniq_id || index} className="animate-fade-in-up" style={{animationDelay: `${index * 50}ms`}}>
                    <ProductCard 
                      product={product} 
                    />
                  </div>
                ))}
              </div>
          ) : (
            <div className="text-center py-20 bg-white rounded-2xl shadow-sm border border-gray-100">
              <div className="animate-bounce mb-6">
                <div className="text-gray-300 text-8xl mb-4">🔍</div>
              </div>
              <h3 className="text-2xl font-serif font-bold text-gray-900 mb-4">
                {searchQuery ? 'No results found' : 'No products found'}
              </h3>
              <p className="text-gray-600 mb-8 text-lg max-w-md mx-auto leading-relaxed">
                {searchQuery 
                  ? `We couldn't find any furniture matching "${searchQuery}". Try adjusting your search or filters.`
                  : 'We couldn\'t find any furniture matching your criteria. Try adjusting your filters.'
                }
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                {(searchQuery || Object.values(filters).some(f => f && f.length > 0)) && (
                  <button
                    onClick={() => {
                      setSearchQuery('');
                      setFilters({
                        category: '',
                        priceRange: [0, 10000],
                        material: '',
                        brand: ''
                      });
                      fetchProducts();
                    }}
                    className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-8 py-4 rounded-xl font-semibold hover:from-amber-600 hover:to-orange-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                  >
                    Clear All Filters
                  </button>
                )}
                <Link
                  to="/"
                  className="border-2 border-amber-500 text-amber-600 px-8 py-4 rounded-xl font-semibold hover:bg-amber-50 transition-all duration-300 inline-flex items-center justify-center"
                >
                  Back to Home
                </Link>
              </div>
            </div>
          )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Shop;