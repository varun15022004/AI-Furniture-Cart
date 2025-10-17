import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import { FiShoppingCart, FiHeart, FiEye } from 'react-icons/fi';

const ProductCard = ({ product }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const { addToCart, isInCart } = useCart();

  // Parse images from the product data
  const getProductImage = () => {
    // First try the images field from CSV
    if (product.images) {
      try {
        const images = typeof product.images === 'string' 
          ? JSON.parse(product.images.replace(/'/g, '"'))
          : product.images;
        if (Array.isArray(images) && images.length > 0) {
          return images[0].trim();
        }
      } catch (e) {
        console.warn('Error parsing product images:', e);
      }
    }
    // Try images_clean as fallback
    if (product.images_clean) {
      try {
        const images = JSON.parse(product.images_clean.replace(/'/g, '"'));
        if (Array.isArray(images) && images.length > 0) {
          return images[0];
        }
      } catch (e) {
        console.warn('Error parsing product images_clean:', e);
      }
    }
    // Return null instead of placeholder to show no image state
    return null;
  };

  // Get the main category for display
  const getMainCategory = () => {
    if (product.categories_clean) {
      try {
        const categories = JSON.parse(product.categories_clean.replace(/'/g, '"'));
        if (Array.isArray(categories) && categories.length > 0) {
          return categories[0];
        }
        return categories;
      } catch (e) {
        return product.categories_clean;
      }
    }
    return 'General';
  };

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(product);
  };

  const productPrice = parseFloat(product.price_num) || 0;
  const similarityScore = product.similarity_score;

  return (
    <Link to={`/product/${product.uniq_id}`} className="group block">
      <div className="bg-white rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 group-hover:border-amber-300 transform group-hover:-translate-y-2 group-hover:scale-105">
        {/* Image Container */}
        <div className="relative h-72 bg-gradient-to-br from-gray-50 to-gray-100 overflow-hidden">
          {getProductImage() && !imageError ? (
            <img
              src={getProductImage()}
              alt={product.title || 'Product'}
              onLoad={() => setImageLoaded(true)}
              onError={() => setImageError(true)}
              className={`w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out ${
                imageLoaded ? 'opacity-100' : 'opacity-0'
              }`}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
              <div className="text-center p-6">
                <div className="text-6xl mb-3 animate-bounce">🛋️</div>
                <div className="text-gray-500 text-sm font-medium">Beautiful Furniture</div>
                <div className="text-gray-400 text-xs mt-1">Image coming soon</div>
              </div>
            </div>
          )}

          {/* Loading placeholder */}
          {!imageLoaded && !imageError && (
            <div className="absolute inset-0 bg-gray-200 animate-pulse"></div>
          )}
          
          {/* Quick Actions */}
          <div className="absolute top-3 right-3 flex flex-col space-y-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <button 
              className="p-2 bg-white rounded-full shadow-md hover:bg-amber-50 transition-colors"
              onClick={(e) => e.preventDefault()}
            >
              <FiHeart size={16} className="text-gray-600 hover:text-red-500" />
            </button>
            <button 
              onClick={handleAddToCart}
              className={`p-2 bg-white rounded-full shadow-md hover:bg-amber-50 transition-colors ${
                isInCart(product.uniq_id) ? 'bg-amber-50' : ''
              }`}
            >
              <FiShoppingCart size={16} className={`${
                isInCart(product.uniq_id) ? 'text-amber-600' : 'text-gray-600'
              }`} />
            </button>
            <Link 
              to={`/product/${product.uniq_id}`}
              className="p-2 bg-white rounded-full shadow-md hover:bg-amber-50 transition-colors"
              onClick={(e) => e.stopPropagation()}
            >
              <FiEye size={16} className="text-gray-600" />
            </Link>
          </div>

          {/* Hover Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

          {/* Category Badge */}
          <span className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm text-gray-700 px-3 py-2 text-xs font-bold rounded-xl shadow-lg border border-white/20">
            {getMainCategory()}
          </span>

          {/* Similarity Score Badge (for search results) */}
          {similarityScore && (
            <span className="absolute top-4 right-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white px-3 py-2 text-xs font-bold rounded-xl shadow-lg">
              ✨ {(similarityScore * 100).toFixed(0)}% Match
            </span>
          )}

          {/* AI Generated Badge */}
          {product.ai_description && (
            <span className="absolute bottom-4 right-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-3 py-2 text-xs font-bold rounded-xl shadow-lg animate-pulse">
              🤖 AI Enhanced
            </span>
          )}
        </div>

        {/* Content */}
        <div className="p-6">
          <h3 className="font-bold text-gray-900 mb-3 line-clamp-2 group-hover:text-amber-600 transition-colors text-lg leading-tight">
            {product.title || 'Untitled Product'}
          </h3>
          
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
            {product.ai_description || product.description || 'No description available'}
          </p>

          {/* Product Details */}
          <div className="flex flex-wrap gap-1 mb-3">
            {product.material_norm && (
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                {product.material_norm}
              </span>
            )}
            {product.brand_norm && (
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                {product.brand_norm}
              </span>
            )}
          </div>
          
          <div className="flex justify-between items-center">
            <div className="flex flex-col">
              {productPrice > 0 ? (
                <span className="text-lg font-bold text-gray-900">
                  ${productPrice.toFixed(2)}
                </span>
              ) : (
                <span className="text-lg font-bold text-gray-500">
                  Price not available
                </span>
              )}
              
              {/* Original price if different */}
              {product.original_price && parseFloat(product.original_price) > productPrice && (
                <span className="text-sm text-gray-500 line-through">
                  ${parseFloat(product.original_price).toFixed(2)}
                </span>
              )}
            </div>

            <button
              onClick={handleAddToCart}
              className={`px-6 py-3 rounded-xl font-bold text-sm transition-all duration-300 transform hover:scale-105 ${
                isInCart(product.uniq_id)
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
                  : 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 shadow-lg hover:shadow-xl'
              }`}
            >
              {isInCart(product.uniq_id) ? '✓ In Cart' : 'Add to Cart'}
            </button>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ProductCard;