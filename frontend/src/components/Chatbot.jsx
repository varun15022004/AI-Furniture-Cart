import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { FiMessageCircle, FiSend, FiX, FiRefreshCw, FiSettings, FiUser, FiShoppingCart } from 'react-icons/fi';
import ProductCard from './UI/ProductCard';
import { useCart } from '../context/CartContext';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showProducts, setShowProducts] = useState([]);
  const messagesEndRef = useRef(null);
  const { addToCart } = useCart();

  const userId = 'user_' + Date.now(); // Simple user ID for demo

  useEffect(() => {
    // Load initial suggestions
    loadSuggestions();
    
    // Add welcome message
    if (messages.length === 0) {
      setMessages([{
        id: Date.now(),
        type: 'bot',
        content: "Hello! I'm your furniture shopping assistant. How can I help you find the perfect pieces for your home?",
        timestamp: new Date()
      }]);
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSuggestions = async () => {
    try {
      const response = await axios.get('/api/chatbot/suggestions');
      if (response.data.status === 'success') {
        setSuggestions(response.data.suggestions.slice(0, 4)); // Show first 4
      }
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const sendMessage = async (message = null) => {
    const messageText = message || inputMessage.trim();
    if (!messageText) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chatbot/message', {
        message: messageText,
        user_id: userId,
        conversation_history: messages.slice(-5) // Send last 5 messages for context
      });

      if (response.data.status === 'success') {
        // Add bot response
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: response.data.response,
          timestamp: new Date(),
          intent: response.data.intent,
          entities: response.data.entities
        };

        setMessages(prev => [...prev, botMessage]);

        // Show product suggestions if available
        if (response.data.products && response.data.products.length > 0) {
          setShowProducts(response.data.products);
          
          // Add products message
          const productsMessage = {
            id: Date.now() + 2,
            type: 'products',
            products: response.data.products,
            timestamp: new Date()
          };
          
          setMessages(prev => [...prev, productsMessage]);
        }
      } else {
        throw new Error(response.data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: "I'm sorry, I'm having trouble right now. Please try again or use the search feature.",
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const resetConversation = async () => {
    try {
      await axios.post(`/api/chatbot/reset/${userId}`);
      setMessages([{
        id: Date.now(),
        type: 'bot',
        content: "Hi again! How can I help you find furniture today?",
        timestamp: new Date()
      }]);
      setShowProducts([]);
    } catch (error) {
      console.error('Error resetting conversation:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="group bg-gradient-to-r from-amber-500 to-orange-500 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-110 transition-all duration-300 animate-bounce"
          aria-label="Open chat"
        >
          <FiMessageCircle className="w-6 h-6 group-hover:rotate-12 transition-transform" />
          <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
            AI
          </div>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 max-w-[90vw] z-50 animate-scale-in">
      <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-white/20 p-2 rounded-full">
              <FiSettings className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold">Furniture Assistant</h3>
              <p className="text-xs opacity-90">AI-powered recommendations</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={resetConversation}
              className="p-2 hover:bg-white/20 rounded-full transition-colors"
              title="Reset conversation"
            >
              <FiRefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 hover:bg-white/20 rounded-full transition-colors"
              title="Close chat"
            >
              <FiX className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50 to-white">
          {messages.map((message) => (
            <div key={message.id}>
              {message.type === 'user' ? (
                <div className="flex justify-end">
                  <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-2 rounded-2xl rounded-tr-md max-w-xs shadow-md">
                    <div className="flex items-center space-x-2 mb-1">
                      <FiUser className="w-3 h-3" />
                      <span className="text-xs opacity-80">You</span>
                    </div>
                    <p className="text-sm">{message.content}</p>
                  </div>
                </div>
              ) : message.type === 'bot' ? (
                <div className="flex justify-start">
                  <div className={`px-4 py-2 rounded-2xl rounded-tl-md max-w-xs shadow-md ${
                    message.isError 
                      ? 'bg-red-50 border border-red-200 text-red-700'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}>
                    <div className="flex items-center space-x-2 mb-1">
                      <FiSettings className={`w-3 h-3 ${message.isError ? 'text-red-500' : 'text-amber-500'}`} />
                      <span className="text-xs opacity-60">Assistant</span>
                    </div>
                    <p className="text-sm">{message.content}</p>
                  </div>
                </div>
              ) : message.type === 'products' ? (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <FiShoppingCart className="w-4 h-4" />
                    <span className="text-sm font-medium">Product Suggestions:</span>
                  </div>
                  <div className="grid grid-cols-1 gap-3 max-h-64 overflow-y-auto">
                    {message.products.slice(0, 3).map((product, index) => {
                      const getProductImage = () => {
                        if (product.images) {
                          try {
                            const images = typeof product.images === 'string' 
                              ? JSON.parse(product.images.replace(/'/g, '"'))
                              : product.images;
                            if (Array.isArray(images) && images.length > 0) {
                              return images[0].trim();
                            }
                          } catch (e) {
                            console.warn('Error parsing chatbot product images:', e);
                          }
                        }
                        return null;
                      };
                      
                      return (
                        <div
                          key={index}
                          className="bg-white border border-gray-200 rounded-xl p-3 hover:shadow-md transition-shadow"
                        >
                          <div className="flex space-x-3">
                            {/* Product Image */}
                            <div className="w-16 h-16 flex-shrink-0">
                              {getProductImage() ? (
                                <img
                                  src={getProductImage()}
                                  alt={product.title}
                                  className="w-full h-full object-cover rounded-lg"
                                  onError={(e) => {
                                    e.target.style.display = 'none';
                                    e.target.nextSibling.style.display = 'flex';
                                  }}
                                />
                              ) : null}
                              <div 
                                className="w-full h-full bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg flex items-center justify-center"
                                style={{ display: getProductImage() ? 'none' : 'flex' }}
                              >
                                <span className="text-xl">🛋️</span>
                              </div>
                            </div>
                            
                            {/* Product Details */}
                            <div className="flex-1 min-w-0">
                              <h4 className="font-semibold text-gray-900 text-sm mb-1 line-clamp-2">
                                {product.title}
                              </h4>
                              <p className="text-xs text-gray-600 mb-2 line-clamp-1">
                                {product.description}
                              </p>
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-amber-600">
                                  ${parseFloat(product.price || 0).toFixed(2)}
                                </span>
                                <button
                                  onClick={() => {
                                    addToCart({
                                      uniq_id: product.id,
                                      title: product.title,
                                      price_num: product.price,
                                      category: product.category
                                    });
                                  }}
                                  className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-2 py-1 rounded text-xs font-medium hover:from-amber-600 hover:to-orange-600 transition-all"
                                >
                                  Add to Cart
                                </button>
                              </div>
                              {product.reason && (
                                <p className="text-xs text-blue-600 mt-1 italic">
                                  💡 {product.reason}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : null}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 px-4 py-2 rounded-2xl rounded-tl-md">
                <div className="flex items-center space-x-2">
                  <FiSettings className="w-3 h-3 text-amber-500" />
                  <div className="flex space-x-1">
                    <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse"></div>
                    <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse delay-75"></div>
                    <div className="w-1 h-1 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Quick Action Buttons */}
          {messages.length <= 1 && (
            <div className="space-y-3">
              <p className="text-xs text-gray-500 text-center">🛋️ Quick Options:</p>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => sendMessage('Show me chairs')}
                  className="p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-xs text-blue-700 transition-all hover:scale-105"
                >
                  <div className="text-lg mb-1">🪑</div>
                  <div className="font-medium">Chairs</div>
                </button>
                <button
                  onClick={() => sendMessage('Show me sofas')}
                  className="p-3 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg text-xs text-green-700 transition-all hover:scale-105"
                >
                  <div className="text-lg mb-1">🛋️</div>
                  <div className="font-medium">Sofas</div>
                </button>
                <button
                  onClick={() => sendMessage('Show me tables')}
                  className="p-3 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg text-xs text-purple-700 transition-all hover:scale-105"
                >
                  <div className="text-lg mb-1">🏠</div>
                  <div className="font-medium">Tables</div>
                </button>
                <button
                  onClick={() => sendMessage('Show me beds')}
                  className="p-3 bg-pink-50 hover:bg-pink-100 border border-pink-200 rounded-lg text-xs text-pink-700 transition-all hover:scale-105"
                >
                  <div className="text-lg mb-1">🛏️</div>
                  <div className="font-medium">Beds</div>
                </button>
              </div>
              
              <p className="text-xs text-gray-500 text-center mt-3">💡 Or try asking:</p>
              <div className="grid grid-cols-1 gap-2">
                {suggestions.slice(0, 3).map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="text-left p-2 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-lg text-xs text-amber-700 transition-colors"
                  >
                    💬 "{suggestion}"
                  </button>
                ))}
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about furniture..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none text-sm"
              disabled={isLoading}
            />
            <button
              onClick={() => sendMessage()}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-gradient-to-r from-amber-500 to-orange-500 text-white p-2 rounded-xl hover:from-amber-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
            >
              <FiSend className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Powered by AI • Ask about style, price, room, or material
          </p>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;