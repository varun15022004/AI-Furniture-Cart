from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# Import our custom modules
from models.recommendation_model import RecommendationEngine
from models.nlp_processor import NLPProcessor
from models.cv_model import ComputerVisionModel
from models.genai_descriptions import GenAIDescriptionGenerator
from database.vector_db import VectorDatabase
from analytics.analytics_service import AnalyticsService

app = FastAPI(title="Furniture Recommendation API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
recommendation_engine = None
nlp_processor = None
cv_model = None
genai_generator = None
vector_db = None
analytics_service = None

# Pydantic models for API requests/responses
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class RecommendationRequest(BaseModel):
    user_query: str
    max_results: Optional[int] = 5
    filters: Optional[Dict[str, Any]] = {}

class RecommendationResponse(BaseModel):
    products: List[Dict[str, Any]]
    generated_description: str
    search_query: str
    timestamp: str

class AnalyticsResponse(BaseModel):
    total_products: int
    categories_distribution: Dict[str, int]
    price_statistics: Dict[str, float]
    brand_distribution: Dict[str, int]
    material_distribution: Dict[str, int]
    country_distribution: Dict[str, int]
    price_trends: List[Dict[str, Any]]
    category_insights: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    """Initialize all models and services on startup"""
    global recommendation_engine, nlp_processor, cv_model, genai_generator, vector_db, analytics_service
    
    print("Initializing services...")
    
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_furniture_data.csv")
    if not os.path.exists(data_path):
        print("Warning: Sample data not found. Please ensure dataset is available.")
        return
    
    try:
        # Initialize all services
        recommendation_engine = RecommendationEngine(data_path)
        nlp_processor = NLPProcessor()
        cv_model = ComputerVisionModel()
        genai_generator = GenAIDescriptionGenerator()
        vector_db = VectorDatabase()
        analytics_service = AnalyticsService(data_path)
        
        print("All services initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing services: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Furniture Recommendation API is running!", "version": "1.0.0"}

@app.post("/chat/recommend", response_model=RecommendationResponse)
async def chat_recommend(request: ChatMessage):
    """Main chat endpoint for product recommendations"""
    if not recommendation_engine:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        # Process user message with NLP
        processed_query = nlp_processor.process_query(request.message)
        
        # Get recommendations using multiple methods
        recommendations = recommendation_engine.get_recommendations(
            query=processed_query,
            max_results=5
        )
        
        # Generate creative descriptions using GenAI
        generated_description = genai_generator.generate_description(
            recommendations, processed_query
        )
        
        # Store interaction in vector database
        vector_db.store_interaction(request.message, recommendations)
        
        return RecommendationResponse(
            products=recommendations,
            generated_description=generated_description,
            search_query=processed_query,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Get product recommendations based on query and filters"""
    if not recommendation_engine:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        recommendations = recommendation_engine.get_recommendations(
            query=request.user_query,
            max_results=request.max_results,
            filters=request.filters
        )
        
        return {"recommendations": recommendations, "total": len(recommendations)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get comprehensive analytics about the furniture dataset"""
    if not analytics_service:
        raise HTTPException(status_code=503, detail="Analytics service not initialized")
    
    try:
        analytics_data = analytics_service.generate_comprehensive_analytics()
        return analytics_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

@app.get("/analytics/categories")
async def get_category_analytics():
    """Get detailed category analytics"""
    if not analytics_service:
        raise HTTPException(status_code=503, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_category_analytics()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting category analytics: {str(e)}")

@app.get("/analytics/prices")
async def get_price_analytics():
    """Get detailed price analytics"""
    if not analytics_service:
        raise HTTPException(status_code=503, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_price_analytics()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting price analytics: {str(e)}")

@app.post("/classify-image")
async def classify_image(file: UploadFile = File(...)):
    """Classify furniture type from uploaded image"""
    if not cv_model:
        raise HTTPException(status_code=503, detail="Computer Vision model not initialized")
    
    try:
        # Read and process the uploaded image
        image_data = await file.read()
        
        # Classify the image
        classification_result = cv_model.classify_furniture(image_data)
        
        return {"classification": classification_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying image: {str(e)}")

@app.get("/similar-products/{product_id}")
async def get_similar_products(product_id: str, limit: int = 5):
    """Get similar products based on product ID"""
    if not recommendation_engine:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        similar_products = recommendation_engine.get_similar_products(product_id, limit)
        return {"similar_products": similar_products}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar products: {str(e)}")

@app.get("/search")
async def search_products(
    query: str,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    material: Optional[str] = None,
    color: Optional[str] = None,
    limit: int = 10
):
    """Advanced product search with filters"""
    if not recommendation_engine:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        filters = {}
        if category:
            filters['categories'] = category
        if min_price is not None:
            filters['min_price'] = min_price
        if max_price is not None:
            filters['max_price'] = max_price
        if brand:
            filters['brand'] = brand
        if material:
            filters['material'] = material
        if color:
            filters['color'] = color
            
        results = recommendation_engine.search_products(query, filters, limit)
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")

@app.get("/products/{product_id}")
async def get_product_details(product_id: str):
    """Get detailed information about a specific product"""
    if not recommendation_engine:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        product = recommendation_engine.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        return {"product": product}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting product details: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)