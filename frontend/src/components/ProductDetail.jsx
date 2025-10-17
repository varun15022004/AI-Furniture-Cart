import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import axios from 'axios';
import { FiTruck, FiShield, FiArrowLeft, FiHeart, FiShare2 } from 'react-icons/fi';
import LoadingSpinner from './UI/LoadingSpinner';

const ProductDetail = () => {
  const { id } = useParams();
  const { addToCart } = useCart();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/products/${id}`);
      setProduct(response.data.data);
    } catch (error) {
      console.error('Error fetching product:', error);
      setError('Product not found');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (product) {
      for (let i = 0; i < quantity; i++) {
        addToCart(product);
      }
      alert('Product added to cart!');
    }
  };

  if (loading) return <LoadingSpinner message="Loading product..." />;
  
  if (error || !product) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <div className="text-gray-400 text-6xl mb-4">📦</div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Product not found</h2>
        <p className="text-gray-600 mb-8">The product you're looking for doesn't exist or has been removed.</p>
        <Link
          to="/shop"
          className="bg-amber-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-amber-700 transition-colors"
        >
          Back to Shop
        </Link>
      </div>
    );
  }

  const images = product.images_clean ? 
    (() => {
      try {
        const parsed = JSON.parse(product.images_clean.replace(/'/g, '"'));
        return Array.isArray(parsed) ? parsed : [parsed];
      } catch {
        return [];
      }
    })() : [];

  const getMainCategory = () => {
    if (product.categories_clean) {
      try {
        const categories = JSON.parse(product.categories_clean.replace(/'/g, '"'));
        return Array.isArray(categories) ? categories[0] : categories;
      } catch {
        return product.categories_clean;
      }
    }
    return 'General';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-8">
        <Link to="/" className="hover:text-amber-600">Home</Link>
        <span>/</span>
        <Link to="/shop" className="hover:text-amber-600">Shop</Link>
        <span>/</span>
        <span className="text-gray-900">{product.title}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Product Images */}
        <div>
          <div className="bg-gray-100 rounded-2xl p-8 mb-4 aspect-square flex items-center justify-center">
            {images.length > 0 ? (
              <img
                src={images[selectedImage] || images[0]}
                alt={product.title}
                className="max-w-full max-h-full object-contain"
                onError={(e) => {
                  e.target.src = `https://via.placeholder.com/600x600/f3f4f6/9ca3af?text=${encodeURIComponent(product.title || 'Product')}`;
                }}
              />
            ) : (
              <div className="text-center">
                <div className="text-gray-400 text-6xl mb-4">🛋️</div>
                <div className="text-gray-500">No Image Available</div>
              </div>
            )}
          </div>
          {images.length > 1 && (
            <div className="grid grid-cols-4 gap-4">
              {images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(index)}
                  className={`bg-gray-100 rounded-lg p-2 border-2 aspect-square ${
                    selectedImage === index ? 'border-amber-600' : 'border-transparent'
                  }`}
                >
                  <img
                    src={image}
                    alt={`${product.title} view ${index + 1}`}
                    className="w-full h-full object-cover rounded"
                    onError={(e) => {
                      e.target.src = `https://via.placeholder.com/100x100/f3f4f6/9ca3af?text=${index + 1}`;
                    }}
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div>
          <div className="mb-6">
            <span className="inline-block bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-sm font-medium mb-4">
              {getMainCategory()}
            </span>
            <h1 className="text-3xl font-serif font-bold text-gray-900 mb-4">
              {product.title}
            </h1>
            <div className="flex items-center space-x-4 mb-4">
              <span className="text-3xl font-bold text-gray-900">
                ${parseFloat(product.price_num || 0).toFixed(2)}
              </span>
              {product.original_price && parseFloat(product.original_price) > parseFloat(product.price_num || 0) && (
                <span className="text-xl text-gray-500 line-through">
                  ${parseFloat(product.original_price).toFixed(2)}
                </span>
              )}
            </div>
          </div>

          {/* Description */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
            <p className="text-gray-600 leading-relaxed">
              {product.ai_description || product.description || 'No description available for this product.'}
            </p>
          </div>

          {/* Product Details */}
          <div className="mb-6 space-y-3">
            {product.material_norm && (
              <div className="flex">
                <span className="text-gray-600 w-24">Material:</span>
                <span className="text-gray-900 capitalize">{product.material_norm}</span>
              </div>
            )}
            {product.brand_norm && (
              <div className="flex">
                <span className="text-gray-600 w-24">Brand:</span>
                <span className="text-gray-900">{product.brand_norm}</span>
              </div>
            )}
            {product.color_norm && (
              <div className="flex">
                <span className="text-gray-600 w-24">Color:</span>
                <span className="text-gray-900 capitalize">{product.color_norm}</span>
              </div>
            )}
          </div>

          {/* Quantity and Add to Cart */}
          <div className="mb-6">
            <div className="flex items-center space-x-4 mb-4">
              <span className="text-gray-700">Quantity:</span>
              <div className="flex items-center border border-gray-300 rounded-lg">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-2 text-gray-600 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                >
                  -
                </button>
                <span className="px-4 py-2 text-gray-900 min-w-12 text-center">{quantity}</span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="px-4 py-2 text-gray-600 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                >
                  +
                </button>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={handleAddToCart}
                className="flex-1 bg-amber-600 text-white py-4 rounded-lg font-semibold hover:bg-amber-700 transition-colors"
              >
                Add to Cart
              </button>
              <button className="p-4 border border-gray-300 rounded-lg hover:border-amber-600 transition-colors">
                <FiHeart size={24} className="text-gray-600" />
              </button>
              <button className="p-4 border border-gray-300 rounded-lg hover:border-amber-600 transition-colors">
                <FiShare2 size={24} className="text-gray-600" />
              </button>
            </div>
          </div>

          {/* Features */}
          <div className="border-t border-gray-200 pt-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <FiTruck className="w-6 h-6 text-amber-600" />
                <div>
                  <div className="font-semibold">Free Shipping</div>
                  <div className="text-sm text-gray-600">On orders over $499</div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <FiShield className="w-6 h-6 text-amber-600" />
                <div>
                  <div className="font-semibold">2-Year Warranty</div>
                  <div className="text-sm text-gray-600">Quality guaranteed</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;