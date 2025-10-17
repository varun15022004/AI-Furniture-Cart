from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import asyncio
import io

try:
    from ai_engine import AdvancedAIEngine
    AI_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI Engine not available: {e}")
    AI_ENGINE_AVAILABLE = False

try:
    from chatbot_engine import FurnitureChatbot
    CHATBOT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chatbot not available: {e}")
    CHATBOT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FurniCraft E-Commerce API",
    description="AI-Powered Furniture Recommendation System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found", "status": "error"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status": "error"}
    )

# Global variables
products_df = None
ai_engine = None
chatbot = None

# Initialize AI Engine
if AI_ENGINE_AVAILABLE:
    try:
        ai_engine = AdvancedAIEngine()
        logger.info("AI Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI Engine: {e}")
        ai_engine = None

# Initialize Chatbot
if CHATBOT_AVAILABLE:
    try:
        chatbot = FurnitureChatbot(ai_engine)
        logger.info("Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Chatbot: {e}")
        chatbot = None

def load_products():
    """Load products from CSV file"""
    global products_df
    try:
        products_df = pd.read_csv("data/clean_products.csv")
        
        # Clean and normalize the data
        products_df['price_num'] = products_df['price'].astype(str).str.replace('$', '').str.replace(',', '').str.replace('nan', '')
        products_df['price_num'] = pd.to_numeric(products_df['price_num'], errors='coerce')
        
        # Fill missing values
        products_df = products_df.fillna('')
        
        logger.info(f"Loaded {len(products_df)} products")
        return products_df
    except Exception as e:
        logger.error(f"Error loading products: {e}")
        return pd.DataFrame()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "FurniCraft E-Commerce API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/products")
async def get_all_products(limit: int = 20):
    """Get all products"""
    try:
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            return {"data": [], "total": 0, "message": "No products available"}
        
        # Get limited products
        products = products_df.head(limit).fillna('').to_dict('records')
        
        return {"data": products, "total": len(products), "status": "success"}
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return {"data": [], "total": 0, "error": str(e), "status": "error"}

@app.get("/api/products/search")
async def search_products(q: Optional[str] = None, limit: int = 20):
    """Search products"""
    try:
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            return {"data": [], "total": 0, "message": "No products available"}
        
        if q:
            query_lower = q.lower()
            matched = products_df[
                products_df['title'].astype(str).str.lower().str.contains(query_lower, na=False) |
                products_df['description'].astype(str).str.lower().str.contains(query_lower, na=False)
            ].head(limit)
        else:
            matched = products_df.head(limit)
        
        products = matched.fillna('').to_dict('records')
        return {"data": products, "total": len(products), "query": q or "", "status": "success"}
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return {"data": [], "total": 0, "error": str(e), "status": "error"}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get single product by ID"""
    try:
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            raise HTTPException(status_code=404, detail="No products available")
        
        product = products_df[products_df['uniq_id'] == product_id]
        
        if product.empty:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_dict = product.iloc[0].fillna('').to_dict()
        return {"data": product_dict, "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}/recommendations")
async def get_product_recommendations(product_id: str, limit: int = 10):
    """Get recommendations for a specific product"""
    try:
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            return {"data": [], "total": 0, "message": "No products available"}
        
        # Find the product
        product = products_df[products_df['uniq_id'] == product_id]
        if product.empty:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Simple category-based recommendations
        product_category = product.iloc[0].get('categories', '')
        if product_category:
            similar_products = products_df[
                (products_df['categories'].astype(str).str.contains(str(product_category), na=False)) &
                (products_df['uniq_id'] != product_id)
            ].head(limit)
        else:
            # Random products if no category
            similar_products = products_df[products_df['uniq_id'] != product_id].sample(min(limit, len(products_df)-1))
        
        recommendations = similar_products.fillna('').to_dict('records')
        return {
            "data": recommendations, 
            "total": len(recommendations), 
            "product_id": product_id,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations for {product_id}: {e}")
        return {"data": [], "total": 0, "error": str(e), "status": "error"}

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    try:
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            return {
                "total_products": 0,
                "average_price": 0,
                "message": "No data available"
            }
        
        price_data = pd.to_numeric(products_df.get('price_num', []), errors='coerce').dropna()
        
        return {
            "total_products": len(products_df),
            "average_price": float(price_data.mean()) if not price_data.empty else 0,
            "median_price": float(price_data.median()) if not price_data.empty else 0,
            "min_price": float(price_data.min()) if not price_data.empty else 0,
            "max_price": float(price_data.max()) if not price_data.empty else 0,
            "status": "success"
        }
            
    except Exception as e:
        logger.error(f"Error fetching analytics overview: {e}")
        return {"error": str(e), "total_products": 0, "status": "error"}

class AIDescriptionRequest(BaseModel):
    product_name: str
    category: Optional[str] = None
    material: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[str] = None

@app.post("/api/ai/generate-description")
async def generate_description(request: AIDescriptionRequest):
    """Generate AI description for a product"""
    try:
        # Simple template-based description
        description = f"Premium {request.product_name}"
        if request.material:
            description += f" crafted from high-quality {request.material}"
        if request.category:
            description += f". This {request.category.lower()} combines"
        else:
            description += f". This furniture piece combines"
        description += " style and functionality to enhance your living space."
        if request.brand:
            description += f" From {request.brand}, known for quality and design."
        if request.price:
            description += f" Available for {request.price}."
        
        return {
            "description": description,
            "method": "template",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        return {
            "description": f"Beautiful {request.product_name} for your home.",
            "error": str(e),
            "method": "fallback",
            "status": "error"
        }

@app.get("/api/analytics/categories")
async def get_category_analytics():
    """Get category analytics"""
    try:
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            return {"data": [], "message": "No data available"}
        
        # Simple category count
        categories = products_df['categories'].value_counts().head(10)
        category_data = []
        for category, count in categories.items():
            if pd.notna(category) and category.strip():
                category_data.append({
                    "category": category,
                    "count": int(count)
                })
        
        return {"data": category_data, "status": "success"}
        
    except Exception as e:
        logger.error(f"Error fetching category analytics: {e}")
        return {"data": [], "error": str(e), "status": "error"}

@app.get("/api/analytics/brands")
async def get_brand_analytics():
    """Get brand analytics"""
    try:
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            return {"data": [], "message": "No data available"}
        
        # Simple brand count
        brands = products_df['brand'].value_counts().head(10)
        brand_data = []
        for brand, count in brands.items():
            if pd.notna(brand) and brand.strip():
                brand_data.append({
                    "brand": brand,
                    "count": int(count)
                })
        
        return {"data": brand_data, "status": "success"}
        
    except Exception as e:
        logger.error(f"Error fetching brand analytics: {e}")
        return {"data": [], "error": str(e), "status": "error"}

@app.get("/api/analytics/price-distribution")
async def get_price_distribution():
    """Get price distribution analytics"""
    try:
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            return {"data": [], "message": "No data available"}
        
        price_data = pd.to_numeric(products_df.get('price_num', []), errors='coerce').dropna()
        
        if price_data.empty:
            return {"data": [], "message": "No price data available"}
        
        # Create 5 price ranges
        min_price = price_data.min()
        max_price = price_data.max()
        
        ranges = []
        if max_price > min_price:
            step = (max_price - min_price) / 5
            for i in range(5):
                range_min = min_price + (i * step)
                range_max = min_price + ((i + 1) * step)
                count = len(price_data[(price_data >= range_min) & (price_data < range_max)])
                ranges.append({
                    "range": f"${range_min:.0f} - ${range_max:.0f}",
                    "count": int(count)
                })
        
        return {"data": ranges, "status": "success"}
        
    except Exception as e:
        logger.error(f"Error fetching price distribution: {e}")
        return {"data": [], "error": str(e), "status": "error"}

# Advanced AI-Powered Endpoints

@app.post("/api/ai/semantic-search")
async def semantic_search(request: dict):
    """Semantic search using AI embeddings"""
    try:
        if not ai_engine:
            # Fallback to simple search
            query = request.get('query', '')
            return await search_products(query, request.get('limit', 10))
        
        query = request.get('query', '')
        filters = request.get('filters', {})
        limit = request.get('limit', 10)
        
        results = ai_engine.semantic_search(query, limit, filters)
        
        return {
            "data": results,
            "total": len(results),
            "query": query,
            "method": "semantic_search",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return {"data": [], "error": str(e), "status": "error"}

@app.post("/api/ai/personalized-recommendations")
async def get_personalized_recommendations(request: dict):
    """Get personalized recommendations for a user"""
    try:
        if not ai_engine:
            # Fallback to simple recommendations
            return {"data": [], "message": "AI recommendations not available"}
        
        user_id = request.get('user_id', 'anonymous')
        context = request.get('context', {})
        limit = request.get('limit', 10)
        
        recommendations = ai_engine.get_personalized_recommendations(user_id, context, limit)
        
        # Format for frontend
        formatted_recs = []
        for rec in recommendations:
            product_id = rec.get('product_id')
            metadata = rec.get('metadata', {})
            
            formatted_recs.append({
                'uniq_id': product_id,
                'title': metadata.get('title', ''),
                'category': metadata.get('category', ''),
                'price_num': metadata.get('price', 0),
                'ai_description': metadata.get('ai_description', ''),
                'similarity_score': rec.get('similarity', 0),
                'personal_score': rec.get('personal_score', 0),
                'reason': rec.get('reason', '')
            })
        
        return {
            "data": formatted_recs,
            "total": len(formatted_recs),
            "user_id": user_id,
            "method": "personalized_ai",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        return {"data": [], "error": str(e), "status": "error"}

@app.post("/api/ai/user-interaction")
async def track_user_interaction(request: dict):
    """Track user interaction for personalization"""
    try:
        if not ai_engine:
            return {"status": "success", "message": "Tracking not available"}
        
        user_id = request.get('user_id', 'anonymous')
        product_id = request.get('product_id', '')
        interaction_type = request.get('interaction_type', 'view')
        context = request.get('context', {})
        
        ai_engine.update_user_interaction(user_id, product_id, interaction_type, context)
        
        return {
            "status": "success",
            "message": "Interaction tracked",
            "user_id": user_id,
            "product_id": product_id,
            "interaction_type": interaction_type
        }
        
    except Exception as e:
        logger.error(f"Error tracking user interaction: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/api/ai/process-products")
async def process_products_with_ai():
    """Process all products with AI features"""
    try:
        if not ai_engine:
            return {"error": "AI Engine not available", "status": "error"}
        
        global products_df
        if products_df is None:
            products_df = load_products()
        
        if products_df.empty:
            return {"error": "No products to process", "status": "error"}
        
        processed_count = 0
        errors = []
        
        # Process first 50 products to avoid timeout
        sample_products = products_df.head(50)
        
        for _, product_row in sample_products.iterrows():
            try:
                product_data = product_row.to_dict()
                result = ai_engine.process_product(product_data)
                
                if 'error' not in result:
                    processed_count += 1
                else:
                    errors.append(f"Product {product_data.get('uniq_id', 'unknown')}: {result['error']}")
                    
            except Exception as e:
                errors.append(f"Product {product_row.get('uniq_id', 'unknown')}: {str(e)}")
        
        return {
            "processed_count": processed_count,
            "total_products": len(sample_products),
            "errors": errors[:5],  # Return first 5 errors
            "status": "success" if processed_count > 0 else "error"
        }
        
    except Exception as e:
        logger.error(f"Error processing products with AI: {e}")
        return {"error": str(e), "status": "error"}

@app.get("/api/ai/analytics")
async def get_ai_analytics():
    """Get AI-powered analytics insights"""
    try:
        if not ai_engine:
            return {"error": "AI Engine not available", "status": "error"}
        
        insights = ai_engine.get_analytics_insights()
        
        return {
            "data": insights,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting AI analytics: {e}")
        return {"error": str(e), "status": "error"}

@app.post("/api/ai/enhanced-description")
async def generate_enhanced_description(request: dict):
    """Generate enhanced AI description for a product"""
    try:
        if not ai_engine:
            # Fallback to simple template
            product_name = request.get('product_name', 'Premium Furniture')
            return {
                "description": f"Beautiful {product_name} that combines style and functionality.",
                "method": "fallback",
                "status": "success"
            }
        
        product_id = request.get('product_id')
        target_audience = request.get('target_audience', 'general')
        
        # Get product data
        global products_df
        if products_df is None:
            products_df = load_products()
        
        product_data = None
        if product_id and not products_df.empty:
            product_row = products_df[products_df['uniq_id'] == product_id]
            if not product_row.empty:
                product_data = product_row.iloc[0].to_dict()
        
        if not product_data:
            product_data = request.get('product_data', {})
        
        # Process with AI
        result = ai_engine.process_product(product_data)
        
        return {
            "description": result.get('ai_description', 'Beautiful furniture piece for your home.'),
            "image_analysis": result.get('image_analysis'),
            "method": "ai_enhanced",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating enhanced description: {e}")
        return {
            "description": "Beautiful furniture piece for your home.",
            "error": str(e),
            "method": "fallback",
            "status": "error"
        }

# Chatbot Endpoints

@app.post("/api/chatbot/message")
async def chatbot_message(request: dict):
    """Process chatbot message and get response with product suggestions"""
    try:
        if not chatbot:
            return {
                "response": "I'm sorry, the chatbot service is currently unavailable. Please try using the search instead.",
                "products": [],
                "status": "error"
            }
        
        message = request.get('message', '')
        user_id = request.get('user_id', 'anonymous')
        conversation_history = request.get('conversation_history', [])
        
        if not message.strip():
            return {
                "response": "Please tell me what furniture you're looking for!",
                "products": [],
                "status": "error"
            }
        
        # Process message with chatbot
        result = chatbot.process_message(message, user_id, conversation_history)
        
        return {
            "response": result.get('response', ''),
            "products": result.get('products', []),
            "intent": result.get('intent', ''),
            "entities": result.get('entities', {}),
            "has_suggestions": result.get('has_suggestions', False),
            "conversation_id": result.get('conversation_id', user_id),
            "timestamp": result.get('timestamp'),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing chatbot message: {e}")
        return {
            "response": "I'm sorry, I encountered an error. Please try again.",
            "products": [],
            "error": str(e),
            "status": "error"
        }

@app.get("/api/chatbot/conversation/{user_id}")
async def get_conversation_summary(user_id: str):
    """Get conversation summary and user preferences"""
    try:
        if not chatbot:
            return {"preferences": {}, "status": "error"}
        
        summary = chatbot.get_conversation_summary(user_id)
        
        return {
            "data": summary,
            "user_id": user_id,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation summary: {e}")
        return {"error": str(e), "status": "error"}

@app.post("/api/chatbot/reset/{user_id}")
async def reset_conversation(user_id: str):
    """Reset conversation for a user"""
    try:
        if not chatbot:
            return {"status": "error", "message": "Chatbot not available"}
        
        chatbot.reset_conversation(user_id)
        
        return {
            "status": "success",
            "message": f"Conversation reset for user {user_id}",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        return {"error": str(e), "status": "error"}

@app.get("/api/chatbot/suggestions")
async def get_chatbot_suggestions():
    """Get suggested questions/prompts for the chatbot"""
    try:
        suggestions = [
            "Show me modern living room furniture under $800",
            "I need ergonomic office chairs with good back support",
            "What dining sets work best for small apartments?",
            "Find me scandinavian style bedroom furniture",
            "I want leather sofas that are pet-friendly",
            "Show me storage solutions for kids' rooms",
            "What are the most popular coffee tables this year?",
            "I need furniture for a home office setup",
            "Find me eco-friendly wooden furniture",
            "What's the best value furniture under $300?",
            "Show me luxury bedroom sets over $1000",
            "I want industrial style furniture for my loft"
        ]
        
        return {
            "suggestions": suggestions,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting chatbot suggestions: {e}")
        return {"error": str(e), "status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)