# 🛋️ Furniture Website Using AI and ML

A comprehensive e-commerce platform for furniture shopping powered by advanced AI and Machine Learning technologies.

## ✨ Features

### 🎯 Core E-Commerce Features
- **Product Catalog**: Browse furniture with advanced filtering
- **AI-Powered Search**: Semantic search understands natural language queries
- **Shopping Cart**: Full cart management with persistent storage
- **Checkout Process**: Multi-step checkout with order summary
- **Product Details**: Comprehensive product pages with image galleries
- **Responsive Design**: Mobile-first design that works on all devices

### 🤖 AI Features
- **Semantic Search**: Vector-based similarity search using sentence transformers
- **Product Recommendations**: AI-powered product suggestions
- **Auto-Generated Descriptions**: AI-enhanced product descriptions
- **Smart Filtering**: Intelligent product categorization

### 📊 Analytics & Insights
- **Business Dashboard**: Analytics overview with key metrics
- **Price Analysis**: Comprehensive price distribution insights
- **Data Quality Reports**: Monitor product data completeness
- **Performance Tracking**: Monitor search and recommendation performance

## 🏗️ Architecture

```
product-recommender/
├── backend/                    # FastAPI backend
│   ├── main.py                # API server and endpoints
│   ├── recommender.py         # AI recommendation engine
│   ├── analytics.py           # Analytics and insights
│   ├── genai.py              # AI description generator
│   ├── requirements.txt       # Python dependencies
│   └── data/
│       └── clean_products.csv # Product dataset
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── context/          # React context providers
│   │   ├── hooks/            # Custom React hooks
│   │   └── App.js            # Main React application
│   └── package.json          # Frontend dependencies
└── notebooks/                 # Jupyter notebooks for analysis








## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

The frontend will be available at `http://localhost:3000`

## 📚 API Documentation

### Core Endpoints

#### Products
- `GET /api/products` - Get all products with optional filtering
- `GET /api/products/{id}` - Get single product by ID
- `GET /api/categories` - Get all product categories
- `GET /api/brands` - Get all product brands
- `GET /api/materials` - Get all product materials

#### AI Features
- `POST /api/recommend` - Get AI-powered product recommendations
- `POST /api/similar` - Get similar products
- `GET /api/search` - Semantic search with filters
- `POST /api/generate-description` - Generate AI product description

#### Analytics
- `GET /api/analytics/overview` - Get business overview analytics
- `GET /api/analytics/price-distribution` - Get price distribution data
- `GET /api/analytics/category-stats` - Get category statistics

### Example API Usage

```javascript
// Search for products
const searchResults = await fetch('http://localhost:8000/api/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'comfortable office chair',
    top_k: 10
  })
});

// Get analytics overview
const analytics = await fetch('http://localhost:8000/api/analytics/overview');
```

## 🛠️ Technologies Used

### Backend
- **FastAPI**: High-performance Python web framework
- **Sentence Transformers**: Vector embeddings for semantic search
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning utilities
- **OpenAI**: Optional AI description generation

### Frontend
- **React 18**: Modern React with hooks and context
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Tailwind CSS**: Utility-first CSS framework
- **React Icons**: Beautiful icon library

### AI & ML
- **Vector Search**: Cosine similarity with sentence embeddings
- **TF-IDF**: Fallback search mechanism
- **Semantic Understanding**: Natural language query processing

## 💡 Key Components

### Backend Components

#### `recommender.py`
- Implements vector-based product search
- Uses sentence transformers for embeddings
- Provides similarity-based recommendations
- Includes fallback search mechanisms

#### `analytics.py`
- Comprehensive business analytics
- Price distribution analysis
- Data quality monitoring
- Category and brand insights

#### `genai.py`
- AI-powered description generation
- OpenAI integration (optional)
- Template-based fallback system

### Frontend Components

#### Core Pages
- **Home**: Landing page with hero section and featured categories
- **Shop**: Product catalog with search and filtering
- **Product Detail**: Individual product pages
- **Cart**: Shopping cart management
- **Checkout**: Multi-step checkout process
- **Analytics**: Business insights dashboard

#### UI Components
- **ProductCard**: Reusable product display component
- **SearchBar**: Semantic search interface
- **FilterSidebar**: Advanced filtering options
- **LoadingSpinner**: Loading state management

## 🎨 Design System

### Colors
- **Primary**: Amber/Orange gradient (#f59e0b to #d97706)
- **Secondary**: Gray scale for content
- **Accent**: Green for success, Red for errors

### Typography
- **Headlines**: Playfair Display (serif)
- **Body**: Inter (sans-serif)

### Layout
- **Mobile-first**: Responsive design principles
- **Grid System**: CSS Grid and Flexbox
- **Spacing**: Consistent spacing scale

## 📊 Dataset

The platform uses furniture product data with the following structure:
- **Product ID**: Unique identifier
- **Title**: Product name
- **Price**: Numeric price value
- **Categories**: Product categories (JSON array)
- **Materials**: Product materials
- **Brands**: Manufacturer information
- **Images**: Product image URLs
- **Descriptions**: Product descriptions

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here  # Optional, for AI descriptions
```

### Customization
- **Colors**: Modify `tailwind.config.js` for custom color schemes
- **API Base URL**: Update in frontend components for production deployment
- **Search Model**: Change sentence transformer model in `recommender.py`

## 🚀 Production Deployment

### Backend Deployment
```bash
# Install production dependencies
pip install gunicorn

# Start with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files
npm install -g serve
serve -s build -l 3000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

Created by Aarushi for demonstrating modern e-commerce development with AI integration.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Review the API documentation at `http://localhost:8000/docs`
- Check the component documentation in the code

---

**Happy Shopping! 🛋️✨**
