import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader, Sparkles, ShoppingBag, Heart, ExternalLink } from 'lucide-react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

function ChatPage() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "🛍️ Welcome to SmartShop Explorer! I'm your AI shopping assistant powered by advanced machine learning, NLP, and computer vision. Tell me what you're looking for and I'll find the perfect products for you!",
      timestamp: new Date(),
      isWelcome: true
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(`session-${Date.now()}`)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentMessage = inputMessage
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat/recommend`, {
        message: currentMessage,
        session_id: sessionId
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.generated_description,
        timestamp: new Date(),
        recommendations: response.data.products,
        searchQuery: response.data.search_query
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Enhanced offline/demo response with better variety
      const sampleRecommendations = [
        {
          uniq_id: "demo-1",
          title: "Ergonomic Office Chair Pro",
          brand: "Herman Miller",
          description: "Premium ergonomic office chair with advanced lumbar support and breathable mesh design.",
          price: 459.00,
          categories: "Office > Chairs",
          material: "Mesh/Aluminum",
          color: "Black",
          similarity_score: 0.95,
          images: "/api/placeholder/300/200"
        },
        {
          uniq_id: "demo-2",
          title: "Modern Oak Dining Table",
          brand: "West Elm",
          description: "Sleek dining table crafted from sustainable oak wood with clean lines and modern aesthetic.",
          price: 699.99,
          categories: "Dining > Tables",
          material: "Oak Wood",
          color: "Natural",
          similarity_score: 0.88,
          images: "/api/placeholder/300/200"
        },
        {
          uniq_id: "demo-3",
          title: "Luxury Velvet Sofa",
          brand: "Pottery Barn",
          description: "Plush velvet sofa with deep cushioning and sophisticated styling for your living room.",
          price: 1299.99,
          categories: "Living Room > Sofas",
          material: "Velvet",
          color: "Navy Blue",
          similarity_score: 0.92,
          images: "/api/placeholder/300/200"
        }
      ]

      const demoMessage = `✨ I found some amazing products for "${currentMessage}"! While I'm working on connecting to our full catalog, here are some premium recommendations that match your style preferences. Each piece is carefully curated for quality and design excellence.`
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: demoMessage,
        timestamp: new Date(),
        recommendations: sampleRecommendations,
        searchQuery: currentMessage,
        isDemo: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const quickSuggestions = [
    "Show me a comfortable office chair",
    "I need a modern coffee table", 
    "Find a cozy reading chair",
    "Looking for a dining table set"
  ]

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion)
    inputRef.current?.focus()
  }

  const ProductCard = ({ product, isDemo }) => (
    <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-slate-700/50 p-4 hover:bg-slate-800/80 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10 product-card group">
      <div className="relative mb-3 overflow-hidden rounded-lg">
        <img
          src={product.images || "/api/placeholder/300/200"}
          alt={product.title}
          className="w-full h-40 object-cover transition-transform duration-300 group-hover:scale-105"
          onError={(e) => {
            e.target.src = "/api/placeholder/300/200"
          }}
        />
        <div className="absolute top-2 right-2">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs px-2 py-1 rounded-full font-medium">
            {Math.round(product.similarity_score * 100)}% match
          </div>
        </div>
        {isDemo && (
          <div className="absolute top-2 left-2">
            <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs px-2 py-1 rounded-full font-medium flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Demo
            </div>
          </div>
        )}
      </div>
      
      <div className="space-y-2">
        <h4 className="font-semibold text-slate-100 group-hover:text-blue-300 transition-colors line-clamp-2">
          {product.title}
        </h4>
        
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-blue-400">{product.brand}</span>
          <div className="h-1 w-1 bg-slate-600 rounded-full"></div>
          <span className="text-xs text-slate-400">{product.material}</span>
        </div>
        
        <p className="text-sm text-slate-300 line-clamp-2 leading-relaxed">
          {product.description}
        </p>
        
        <div className="flex items-center justify-between pt-2 border-t border-slate-700/50">
          <div className="flex flex-col">
            <span className="text-xl font-bold text-blue-400">
              ${product.price?.toFixed(2)}
            </span>
            <span className="text-xs text-slate-500">
              {product.categories?.split(' > ')[0]}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <button className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-red-400 transition-colors">
              <Heart className="w-4 h-4" />
            </button>
            <button className="px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-400 hover:to-purple-500 text-white text-sm font-medium rounded-lg transition-all duration-300 flex items-center gap-1">
              <ExternalLink className="w-4 h-4" />
              View
            </button>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 px-6 py-4">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            AI Product Discovery
          </h1>
          <p className="text-slate-400 mt-1">
            Powered by advanced machine learning and natural language processing
          </p>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} message`}
            >
              <div
                className={`max-w-4xl flex ${
                  message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
                } gap-4`}
              >
                {/* Avatar */}
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    message.type === 'user' 
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600' 
                      : 'bg-gradient-to-r from-green-500 to-teal-600'
                  }`}
                >
                  {message.type === 'user' ? (
                    <User className="w-5 h-5 text-white" />
                  ) : (
                    <Bot className="w-5 h-5 text-white" />
                  )}
                </div>

                {/* Message Content */}
                <div className="flex-1">
                  <div
                    className={`p-4 rounded-2xl ${
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white ml-12'
                        : 'bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 text-slate-100'
                    }`}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  </div>

                  {/* Product Recommendations */}
                  {message.recommendations && message.recommendations.length > 0 && (
                    <div className="mt-4 space-y-4">
                      <div className="flex items-center gap-2">
                        <ShoppingBag className="w-5 h-5 text-blue-400" />
                        <p className="text-sm font-medium text-slate-300">
                          Found {message.recommendations.length} products for you:
                        </p>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {message.recommendations.map((product, index) => (
                          <ProductCard key={index} product={product} isDemo={message.isDemo} />
                        ))}
                      </div>
                    </div>
                  )}

                  <p className="text-xs text-slate-500 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {/* Loading Message */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-4xl flex flex-row gap-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-r from-green-500 to-teal-600">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 p-4 rounded-2xl flex items-center gap-3">
                    <Loader className="w-5 h-5 animate-spin text-blue-400" />
                    <span className="text-slate-300">Finding perfect products for you...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Suggestions */}
      {messages.length <= 1 && (
        <div className="px-6 pb-4">
          <div className="max-w-6xl mx-auto">
            <p className="text-sm text-slate-400 mb-3">Try these suggestions:</p>
            <div className="flex flex-wrap gap-2">
              {quickSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 hover:text-white text-sm rounded-lg border border-slate-700/50 hover:border-slate-600 transition-all duration-300"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-t border-slate-700/50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe what you're looking for... (e.g., 'I need a comfortable modern office chair under $300')"
                className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl p-4 text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 resize-none transition-all duration-300"
                rows="2"
                disabled={isLoading}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-400 hover:to-purple-500 disabled:from-slate-600 disabled:to-slate-700 text-white p-4 rounded-xl transition-all duration-300 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}

export default ChatPage