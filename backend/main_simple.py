from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
import logging
from datetime import datetime

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

# Global variable to store products
products_df = None

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)