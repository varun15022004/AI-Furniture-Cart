from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import logging

from recommender import ProductRecommender
from analytics import AnalyticsEngine
from genai import AIDescriptionGenerator

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components - lazy loading to avoid startup delays
recommender = None
analytics = None
ai_generator = None

def initialize_components():
    """Initialize components lazily"""
    global recommender, analytics, ai_generator
    if recommender is None:
        try:
            recommender = ProductRecommender()
            analytics = AnalyticsEngine()
            ai_generator = AIDescriptionGenerator()
            logger.info("All components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            recommender = "error"
            analytics = "error"
            ai_generator = "error"

# Pydantic models
class RecommendationRequest(BaseModel):
    query: str
    top_k: int = 10

class Product(BaseModel):
    uniq_id: str
    title: str
    price_num: Optional[float] = None
    description: Optional[str] = None
    categories_clean: Optional[str] = None
    material_norm: Optional[str] = None
    brand_norm: Optional[str] = None
    images_clean: Optional[str] = None
    ai_description: Optional[str] = None

class FilterRequest(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    material: Optional[str] = None
    brand: Optional[str] = None
    limit: int = 50

class AIDescriptionRequest(BaseModel):
    product_name: str
    category: Optional[str] = None
    material: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[str] = None

# Global variable to store products
products_df = None

def load_products():
    """Load products from CSV file"""
    global products_df
    try:
        products_df = pd.read_csv("data/clean_products.csv")
        
        # Clean and normalize the data
        # Convert price to numeric
        products_df['price_num'] = products_df['price'].astype(str).str.replace('$', '').str.replace(',', '').str.replace('nan', '')
        products_df['price_num'] = pd.to_numeric(products_df['price_num'], errors='coerce')
        
        # Normalize column names to match expected format
        products_df['categories_clean'] = products_df['categories']
        products_df['images_clean'] = products_df['images']
        products_df['material_norm'] = products_df['material']
        products_df['brand_norm'] = products_df['brand']
        products_df['color_norm'] = products_df['color']
        
        # Fill missing values
        products_df = products_df.fillna('')
        
        logger.info(f"Loaded and processed {len(products_df)} products")
        return products_df
    except Exception as e:
        logger.error(f"Error loading products: {e}")
        return pd.DataFrame()

# Load products on first request
def ensure_data_loaded():
    """Ensure data is loaded"""
    global products_df
    if products_df is None:
        try:
            products_df = load_products()
            logger.info(f"Loaded {len(products_df)} products")
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            products_df = pd.DataFrame()  # Empty dataframe fallback
    return products_df

# API Routes

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
async def get_all_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    material: Optional[str] = None,
    brand: Optional[str] = None,
    limit: int = 50
):
    """Get all products with optional filtering"""
    try:
        df = ensure_data_loaded()
        
        if df.empty:
            return {"products": [], "total": 0, "message": "No products available"}
        
        # Apply filters safely
        if category and 'categories_clean' in df.columns:
            df = df[df['categories_clean'].astype(str).str.contains(category, case=False, na=False)]
        if min_price is not None and 'price_num' in df.columns:
            df = df[pd.to_numeric(df['price_num'], errors='coerce').fillna(0) >= min_price]
        if max_price is not None and 'price_num' in df.columns:
            df = df[pd.to_numeric(df['price_num'], errors='coerce').fillna(0) <= max_price]
        if material and 'material_norm' in df.columns:
            df = df[df['material_norm'].astype(str).str.contains(material, case=False, na=False)]
        if brand and 'brand_norm' in df.columns:
            df = df[df['brand_norm'].astype(str).str.contains(brand, case=False, na=False)]
        
        # Apply limit
        df = df.head(limit)
        
        # Convert to records safely
        products = df.fillna('').to_dict('records')
        
        return {"data": products, "total": len(products), "status": "success"}
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return {"data": [], "total": 0, "error": str(e), "status": "error"}

@app.get("/api/products/search")
async def search_products(q: Optional[str] = None, limit: int = 20):
    """Search products by query"""
    try:
        df = ensure_data_loaded()
        
        if df.empty:
            return {"data": [], "total": 0, "message": "No products available"}
        
        if q:
            query_lower = q.lower()
            matched = df[
                df['title'].astype(str).str.lower().str.contains(query_lower, na=False) |
                df['description'].astype(str).str.lower().str.contains(query_lower, na=False) |
                df['categories_clean'].astype(str).str.lower().str.contains(query_lower, na=False)
            ].head(limit)
        else:
            matched = df.head(limit)
        
        products = matched.fillna('').to_dict('records')
        return {"data": products, "total": len(products), "query": q or "", "status": "success"}
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return {"data": [], "total": 0, "error": str(e), "status": "error"}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get single product by ID"""
    try:
        if products_df is None or products_df.empty:
            load_products()
        
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
        df = ensure_data_loaded()
        
        if df.empty:
            return {"data": [], "total": 0, "message": "No products available"}
        
        # Find the product
        product = df[df['uniq_id'] == product_id]
        if product.empty:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Simple category-based recommendations as fallback
        product_category = product.iloc[0].get('categories_clean', '')
        if product_category:
            similar_products = df[
                (df['categories_clean'].astype(str).str.contains(str(product_category), na=False)) &
                (df['uniq_id'] != product_id)
            ].head(limit)
        else:
            # Random products if no category
            similar_products = df[df['uniq_id'] != product_id].sample(min(limit, len(df)-1))
        
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

@app.post("/api/recommend")
async def recommend_products(request: RecommendationRequest):
    """Get product recommendations based on query"""
    try:
        initialize_components()
        
        # Fallback to simple search if recommender fails
        if recommender == "error" or not recommender:
            df = ensure_data_loaded()
            if df.empty:
                return {"query": request.query, "products": [], "total": 0}
            
            # Simple text search fallback
            query_lower = request.query.lower()
            matched = df[
                df['title'].astype(str).str.lower().str.contains(query_lower, na=False) |
                df['description'].astype(str).str.lower().str.contains(query_lower, na=False)
            ].head(request.top_k)
            
            products = matched.fillna('').to_dict('records')
            return {
                "query": request.query,
                "products": products,
                "total": len(products),
                "method": "fallback_search"
            }
        
        recommendations = recommender.get_recommendations(
            query=request.query,
            top_k=request.top_k
        )
        
        return {
            "query": request.query,
            "products": recommendations,
            "total": len(recommendations),
            "method": "ai_recommendations"
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        # Fallback to simple search
        df = ensure_data_loaded()
        return {"query": request.query, "products": [], "total": 0, "error": str(e)}

@app.post("/api/similar")
async def get_similar_products(product_id: str, top_k: int = 10):
    """Get similar products based on a product ID"""
    try:
        if not recommender:
            raise HTTPException(status_code=503, detail="Recommender not available")
        
        similar_products = recommender.get_similar_products(
            product_id=product_id,
            top_k=top_k
        )
        
        return {
            "product_id": product_id,
            "similar_products": similar_products,
            "total": len(similar_products)
        }
        
    except Exception as e:
        logger.error(f"Error getting similar products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """Get all product categories"""
    try:
        if products_df is None or products_df.empty:
            load_products()
        
        # Extract categories from categories_clean column
        categories = set()
        for cat_str in products_df['categories_clean'].dropna():
            if isinstance(cat_str, str) and cat_str.strip():
                try:
                    # Try to parse as JSON array
                    cat_list = json.loads(cat_str.replace("'", '"'))
                    if isinstance(cat_list, list):
                        categories.update(cat_list)
                    else:
                        categories.add(str(cat_list))
                except:
                    # If not JSON, treat as string
                    categories.add(cat_str)
        
        return {"categories": sorted(list(categories))}
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brands")
async def get_brands():
    """Get all product brands"""
    try:
        if products_df is None or products_df.empty:
            load_products()
        
        brands = products_df['brand_norm'].dropna().unique().tolist()
        return {"brands": sorted(brands)}
        
    except Exception as e:
        logger.error(f"Error fetching brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/materials")
async def get_materials():
    """Get all product materials"""
    try:
        if products_df is None or products_df.empty:
            load_products()
        
        materials = products_df['material_norm'].dropna().unique().tolist()
        return {"materials": sorted(materials)}
        
    except Exception as e:
        logger.error(f"Error fetching materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    try:
        initialize_components()
        df = ensure_data_loaded()
        
        if df.empty:
            return {
                "total_products": 0,
                "average_price": 0,
                "median_price": 0,
                "min_price": 0,
                "max_price": 0,
                "message": "No data available"
            }
        
        # Simple analytics if analytics component fails
        if analytics == "error" or not analytics:
            price_data = pd.to_numeric(df.get('price_num', []), errors='coerce').dropna()
            return {
                "total_products": len(df),
                "average_price": float(price_data.mean()) if not price_data.empty else 0,
                "median_price": float(price_data.median()) if not price_data.empty else 0,
                "min_price": float(price_data.min()) if not price_data.empty else 0,
                "max_price": float(price_data.max()) if not price_data.empty else 0,
                "total_categories": df.get('categories_clean', pd.Series()).nunique(),
                "total_brands": df.get('brand_norm', pd.Series()).nunique(),
                "products_with_images": df.get('images_clean', pd.Series()).notna().sum(),
                "products_with_descriptions": df.get('description', pd.Series()).notna().sum(),
                "method": "simple_analytics"
            }
        
        # Use full analytics if available
        if analytics and analytics != "error":
            analytics.load_data(df)
            overview = analytics.get_overview()
            return overview
            
    except Exception as e:
        logger.error(f"Error fetching analytics overview: {e}")
        return {"error": str(e), "total_products": 0}

@app.post("/api/ai/generate-description")
async def generate_description(request: AIDescriptionRequest):
    """Generate AI description for a product"""
    try:
        initialize_components()
        
        # Simple template-based description as fallback
        if ai_generator == "error" or not ai_generator:
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
        
        # Use AI generator if available
        description = ai_generator.generate_description(
            product_name=request.product_name,
            category=request.category,
            material=request.material,
            brand=request.brand,
            price=request.price
        )
        
        return {
            "description": description,
            "method": "ai_generated",
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

@app.get("/api/analytics/price-distribution")
async def get_price_distribution():
    """Get price distribution analytics"""
    try:
        df = ensure_data_loaded()
        
        if df.empty:
            return {"ranges": [], "message": "No data available"}
        
        price_data = pd.to_numeric(df.get('price_num', []), errors='coerce').dropna()
        
        if price_data.empty:
            return {"ranges": [], "message": "No price data available"}
        
        # Create price ranges
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
                    "min": float(range_min),
                    "max": float(range_max),
                    "count": int(count)
                })
        
        return {
            "ranges": ranges,
            "total_products": len(price_data),
            "avg_price": float(price_data.mean()),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching price distribution: {e}")
        return {"ranges": [], "error": str(e), "status": "error"}

@app.get("/api/analytics/categories")
async def get_category_analytics():
    """Get category analytics"""
    try:
        df = ensure_data_loaded()
        
        if df.empty:
            return {"categories": [], "message": "No data available"}
        
        category_stats = []
        category_counts = {}
        
        for cat_str in df['categories_clean'].dropna():
            if isinstance(cat_str, str) and cat_str.strip():
                try:
                    cat_list = json.loads(cat_str.replace("'", '"'))
                    if isinstance(cat_list, list):
                        for cat in cat_list:
                            category_counts[cat] = category_counts.get(cat, 0) + 1
                    else:
                        cat = str(cat_list)
                        category_counts[cat] = category_counts.get(cat, 0) + 1
                except:
                    category_counts[cat_str] = category_counts.get(cat_str, 0) + 1
        
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            category_stats.append({
                "category": category,
                "count": count,
                "percentage": round((count / len(df)) * 100, 2)
            })
        
        return {
            "categories": category_stats,
            "total_categories": len(category_counts),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching category analytics: {e}")
        return {"categories": [], "error": str(e), "status": "error"}

@app.get("/api/analytics/brands")
async def get_brand_analytics():
    """Get brand analytics"""
    try:
        df = ensure_data_loaded()
        
        if df.empty:
            return {"brands": [], "message": "No data available"}
        
        brand_counts = df['brand_norm'].value_counts().head(10)
        brand_stats = []
        
        for brand, count in brand_counts.items():
            if pd.notna(brand) and brand.strip():
                brand_stats.append({
                    "brand": brand,
                    "count": int(count),
                    "percentage": round((count / len(df)) * 100, 2)
                })
        
        return {
            "brands": brand_stats,
            "total_brands": df['brand_norm'].nunique(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching brand analytics: {e}")
        return {"brands": [], "error": str(e), "status": "error"}

@app.post("/api/generate-description")
async def generate_ai_description(product_id: str):
    """Generate AI description for a product"""
    try:
        if not ai_generator:
            raise HTTPException(status_code=503, detail="AI generator not available")
        
        # Get product details
        product = products_df[products_df['uniq_id'] == product_id]
        if product.empty:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_data = product.iloc[0].to_dict()
        description = await ai_generator.generate_description(product_data)
        
        return {
            "product_id": product_id,
            "ai_description": description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI description: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_products(
    q: str,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 20
):
    """Search products with query and filters"""
    try:
        if not q.strip():
            return await get_all_products(category, min_price, max_price, None, None, limit)
        
        # Use recommender if available, otherwise fall back to simple text search
        if recommender:
            recommendations = await recommender.get_recommendations(query=q, top_k=limit)
            
            # Apply additional filters if needed
            if category or min_price is not None or max_price is not None:
                filtered_recommendations = []
                for product in recommendations:
                    if category and category.lower() not in str(product.get('categories_clean', '')).lower():
                        continue
                    if min_price is not None and product.get('price_num', 0) < min_price:
                        continue
                    if max_price is not None and product.get('price_num', 0) > max_price:
                        continue
                    filtered_recommendations.append(product)
                recommendations = filtered_recommendations
            
            return {
                "query": q,
                "products": recommendations,
                "total": len(recommendations)
            }
        else:
            # Fallback to simple text search
            df = products_df.copy()
            
            # Text search in title and description
            df = df[
                df['title'].str.contains(q, case=False, na=False) |
                df['description'].str.contains(q, case=False, na=False)
            ]
            
            # Apply filters
            if category:
                df = df[df['categories_clean'].str.contains(category, case=False, na=False)]
            if min_price is not None:
                df = df[df['price_num'] >= min_price]
            if max_price is not None:
                df = df[df['price_num'] <= max_price]
            
            df = df.head(limit)
            products = df.fillna('').to_dict('records')
            
            return {
                "query": q,
                "products": products,
                "total": len(products)
            }
            
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
