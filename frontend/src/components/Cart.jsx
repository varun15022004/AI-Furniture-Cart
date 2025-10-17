import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { FiTrash2, FiPlus, FiMinus, FiArrowRight, FiShoppingBag } from 'react-icons/fi';

const Cart = () => {
  const { cart, removeFromCart, updateQuantity, getCartTotal, getShippingCost, getTaxAmount, getFinalTotal, clearCart } = useCart();

  const getProductImage = (product) => {
    if (product.images_clean) {
      try {
        const images = JSON.parse(product.images_clean.replace(/'/g, '"'));
        if (Array.isArray(images) && images.length > 0) {
          return images[0];
        }
      } catch (e) {
        console.warn('Error parsing product images:', e);
      }
    }
    return `https://via.placeholder.com/100x100/f3f4f6/9ca3af?text=${encodeURIComponent(product.title || 'Product')}`;
  };

  if (cart.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <div className="mb-8">
            <FiShoppingBag className="mx-auto text-gray-400 text-6xl mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Your cart is empty</h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Looks like you haven't added any items to your cart yet. Start shopping to find your perfect furniture pieces!
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/shop"
              className="bg-amber-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-amber-700 transition-colors inline-flex items-center justify-center"
            >
              <FiShoppingBag className="mr-2" size={20} />
              Start Shopping
            </Link>
            <Link
              to="/"
              className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-serif font-bold text-gray-900">Shopping Cart</h1>
        <p className="text-gray-600 mt-2">{cart.items.length} item{cart.items.length !== 1 ? 's' : ''} in your cart</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
            {cart.items.map((item, index) => (
              <div key={item.uniq_id} className={`flex items-center p-6 ${index !== cart.items.length - 1 ? 'border-b border-gray-200' : ''}`}>
                <div className="flex-shrink-0">
                  <img
                    src={getProductImage(item)}
                    alt={item.title}
                    className="w-24 h-24 object-cover rounded-lg"
                  />
                </div>
                
                <div className="flex-1 ml-6">
                  <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {item.material_norm && (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {item.material_norm}
                      </span>
                    )}
                    {item.brand_norm && (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {item.brand_norm}
                      </span>
                    )}
                  </div>
                  <p className="text-lg font-semibold text-amber-600">
                    ${parseFloat(item.price_num || 0).toFixed(2)}
                  </p>
                </div>

                <div className="flex items-center space-x-4">
                  {/* Quantity Controls */}
                  <div className="flex items-center border border-gray-300 rounded-lg">
                    <button
                      onClick={() => updateQuantity(item.uniq_id, item.quantity - 1)}
                      className="p-2 text-gray-600 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                    >
                      <FiMinus size={16} />
                    </button>
                    <span className="px-4 py-2 text-gray-900 min-w-12 text-center font-medium">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.uniq_id, item.quantity + 1)}
                      className="p-2 text-gray-600 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                    >
                      <FiPlus size={16} />
                    </button>
                  </div>

                  {/* Item Total */}
                  <div className="text-right min-w-20">
                    <p className="font-semibold text-gray-900">
                      ${(parseFloat(item.price_num || 0) * item.quantity).toFixed(2)}
                    </p>
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => removeFromCart(item.uniq_id)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors rounded-full hover:bg-red-50"
                  >
                    <FiTrash2 size={20} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Cart Actions */}
          <div className="mt-6 flex flex-col sm:flex-row justify-between items-center gap-4">
            <button
              onClick={clearCart}
              className="text-red-600 hover:text-red-700 font-medium text-sm"
            >
              Clear Cart
            </button>
            <Link
              to="/shop"
              className="text-amber-600 hover:text-amber-700 font-medium text-sm"
            >
              ← Continue Shopping
            </Link>
          </div>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sticky top-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Order Summary</h2>
            
            <div className="space-y-4 mb-6">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal ({cart.items.reduce((total, item) => total + item.quantity, 0)} items)</span>
                <span>${getCartTotal().toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Shipping</span>
                <span className={getShippingCost() === 0 ? 'text-green-600 font-medium' : ''}>
                  {getShippingCost() === 0 ? 'Free' : `$${getShippingCost().toFixed(2)}`}
                </span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Tax</span>
                <span>${getTaxAmount().toFixed(2)}</span>
              </div>
              <div className="border-t border-gray-200 pt-4">
                <div className="flex justify-between text-lg font-semibold text-gray-900">
                  <span>Total</span>
                  <span>${getFinalTotal().toFixed(2)}</span>
                </div>
              </div>
            </div>

            {getShippingCost() > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-amber-800">
                  💡 <strong>Tip:</strong> Add ${(499 - getCartTotal()).toFixed(2)} more to get free shipping!
                </p>
              </div>
            )}

            <Link
              to="/checkout"
              className="w-full bg-amber-600 text-white py-4 rounded-lg font-semibold hover:bg-amber-700 transition-colors flex items-center justify-center space-x-2 mb-4"
            >
              <span>Proceed to Checkout</span>
              <FiArrowRight size={20} />
            </Link>

            {/* Security badges */}
            <div className="text-center space-y-3">
              <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center">
                  <span className="text-green-600 mr-1">🔒</span>
                  Secure Checkout
                </div>
                <div className="flex items-center">
                  <span className="mr-1">↩️</span>
                  30-day Returns
                </div>
              </div>
              <div className="text-xs text-gray-500">
                We accept all major credit cards and PayPal
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;