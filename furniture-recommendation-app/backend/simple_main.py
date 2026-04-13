from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import json
from datetime import datetime
import random

# Simple models without external dependencies
app = FastAPI(title="Furniture Recommendation API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class RecommendationResponse(BaseModel):
    products: List[Dict[str, Any]]
    generated_description: str
    search_query: str
    timestamp: str

# Sample furniture data
SAMPLE_FURNITURE_DATA = [
    {
        "uniq_id": "1",
        "title": "Modern Oak Dining Table",
        "brand": "IKEA",
        "description": "A sleek and modern dining table made from sustainable oak wood. Perfect for family gatherings and dinner parties.",
        "price": 299.99,
        "categories": "Dining Room > Dining Tables",
        "material": "Oak Wood",
        "color": "Natural Brown",
        "similarity_score": 0.95
    },
    {
        "uniq_id": "2",
        "title": "Comfortable Office Chair",
        "brand": "Herman Miller",
        "description": "Ergonomic office chair with lumbar support and breathable mesh back. Ideal for long working hours.",
        "price": 459.00,
        "categories": "Office > Chairs",
        "material": "Mesh/Plastic",
        "color": "Black",
        "similarity_score": 0.92
    },
    {
        "uniq_id": "3",
        "title": "Minimalist Bookshelf",
        "brand": "MUJI",
        "description": "Clean-lined bookshelf with 5 adjustable shelves. Made from sustainable pine wood.",
        "price": 189.99,
        "categories": "Living Room > Storage",
        "material": "Pine Wood",
        "color": "White",
        "similarity_score": 0.88
    },
    {
        "uniq_id": "4",
        "title": "Velvet Sofa Set",
        "brand": "West Elm",
        "description": "Luxurious 3-seater velvet sofa with matching cushions. Adds elegance to any living space.",
        "price": 1299.99,
        "categories": "Living Room > Sofas",
        "material": "Velvet/Wood",
        "color": "Navy Blue",
        "similarity_score": 0.90
    },
    {
        "uniq_id": "5",
        "title": "Rustic Coffee Table",
        "brand": "Pottery Barn",
        "description": "Handcrafted coffee table with rustic finish. Features storage drawer and lower shelf.",
        "price": 549.00,
        "categories": "Living Room > Coffee Tables",
        "material": "Reclaimed Wood",
        "color": "Brown",
        "similarity_score": 0.85
    },
    {
        "uniq_id": "6",
        "title": "Memory Foam Mattress",
        "brand": "Casper",
        "description": "Premium memory foam mattress with cooling technology. Available in multiple sizes.",
        "price": 799.99,
        "categories": "Bedroom > Mattresses",
        "material": "Memory Foam",
        "color": "White",
        "similarity_score": 0.87
    }
]

def get_sample_recommendations(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Simple recommendation logic based on keyword matching"""
    query_lower = query.lower()
    scored_products = []
    
    for product in SAMPLE_FURNITURE_DATA:
        score = 0.5  # Base score
        
        # Check for keyword matches
        if any(word in product['title'].lower() for word in query_lower.split()):
            score += 0.3
        if any(word in product['description'].lower() for word in query_lower.split()):
            score += 0.2
        if any(word in product['categories'].lower() for word in query_lower.split()):
            score += 0.2
        
        # Add some randomness
        score += random.uniform(-0.1, 0.1)
        
        product_copy = product.copy()
        product_copy['similarity_score'] = min(score, 0.99)
        scored_products.append(product_copy)
    
    # Sort by score and return top results
    scored_products.sort(key=lambda x: x['similarity_score'], reverse=True)
    return scored_products[:max_results]

def generate_simple_description(products: List[Dict], query: str) -> str:
    """Generate a simple description for the recommendations"""
    if not products:
        return "I'm sorry, I couldn't find any suitable products for your request."
    
    templates = [
        f"Based on your search for '{query}', I found {len(products)} great options! The {products[0]['title']} would be perfect for your needs.",
        f"Here are {len(products)} excellent recommendations for '{query}'. I especially recommend the {products[0]['title']} - it's highly rated!",
        f"Great choice! I found {len(products)} products that match your request. The {products[0]['title']} is a popular option that many customers love."
    ]
    
    return random.choice(templates)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Furniture Recommendation API is running!", "version": "1.0.0"}

@app.post("/chat/recommend", response_model=RecommendationResponse)
async def chat_recommend(request: ChatMessage):
    """Main chat endpoint for product recommendations"""
    try:
        # Get recommendations
        recommendations = get_sample_recommendations(request.message)
        
        # Generate description
        description = generate_simple_description(recommendations, request.message)
        
        return RecommendationResponse(
            products=recommendations,
            generated_description=description,
            search_query=request.message,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/analytics")
async def get_analytics():
    """Get comprehensive analytics data matching PRD format"""
    try:
        # Calculate analytics from sample data
        total_products = len(SAMPLE_FURNITURE_DATA)
        
        # Category distribution
        categories = {}
        for product in SAMPLE_FURNITURE_DATA:
            category = product['categories'].split(' > ')[0]
            categories[category] = categories.get(category, 0) + 1
        
        # Brand distribution
        brands = {}
        for product in SAMPLE_FURNITURE_DATA:
            brand = product['brand']
            brands[brand] = brands.get(brand, 0) + 1
        
        # Material distribution
        materials = {}
        for product in SAMPLE_FURNITURE_DATA:
            material = product.get('material', 'Unknown')
            materials[material] = materials.get(material, 0) + 1
        
        # Color distribution
        colors = {}
        for product in SAMPLE_FURNITURE_DATA:
            color = product.get('color', 'Unknown')
            colors[color] = colors.get(color, 0) + 1
        
        # Price statistics
        prices = [product['price'] for product in SAMPLE_FURNITURE_DATA]
        price_stats = {
            'mean': float(np.mean(prices)),
            'median': float(np.median(prices)),
            'min': float(np.min(prices)),
            'max': float(np.max(prices)),
            'std': float(np.std(prices))
        }
        
        # Price ranges
        price_ranges = [
            {'range': '$0-100', 'count': len([p for p in prices if p <= 100]), 'percentage': 0},
            {'range': '$101-300', 'count': len([p for p in prices if 101 <= p <= 300]), 'percentage': 0},
            {'range': '$301-500', 'count': len([p for p in prices if 301 <= p <= 500]), 'percentage': 0},
            {'range': '$501-1000', 'count': len([p for p in prices if 501 <= p <= 1000]), 'percentage': 0},
            {'range': '$1000+', 'count': len([p for p in prices if p > 1000]), 'percentage': 0}
        ]
        
        # Calculate percentages
        for range_item in price_ranges:
            range_item['percentage'] = round((range_item['count'] / total_products) * 100, 1)
        
        # Popular searches (simulated)
        popular_searches = [
            'office chair', 'dining table', 'sofa', 'desk', 'bookshelf',
            'coffee table', 'bed frame', 'mattress', 'storage'
        ]
        
        # Country distribution (simulated)
        country_dist = {
            'USA': 2,
            'Sweden': 1,
            'Japan': 1,
            'Germany': 1,
            'Unknown': 1
        }
        
        return {
            'totalProducts': total_products,
            'totalCategories': len(categories),
            'totalBrands': len(brands),
            'averagePrice': round(price_stats['mean'], 2),
            'categoryDistribution': categories,
            'priceStatistics': price_stats,
            'brandDistribution': brands,
            'materialDistribution': materials,
            'colorDistribution': colors,
            'countryDistribution': country_dist,
            'priceRanges': price_ranges,
            'popularSearches': popular_searches,
            'categoryInsights': [
                {'category': 'Living Room', 'insight': 'Most popular category with highest price variation'},
                {'category': 'Office', 'insight': 'Growing demand for ergonomic furniture'},
                {'category': 'Bedroom', 'insight': 'Premium materials trending upward'}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

@app.get("/products/{product_id}")
async def get_product_details(product_id: str):
    """Get product details by ID"""
    try:
        for product in SAMPLE_FURNITURE_DATA:
            if product['uniq_id'] == product_id:
                return {"product": product}
        
        raise HTTPException(status_code=404, detail="Product not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting product: {str(e)}")

@app.get("/search")
async def search_products(query: str, limit: int = 10):
    """Search products"""
    try:
        results = get_sample_recommendations(query, limit)
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)