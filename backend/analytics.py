import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def __init__(self):
        """Initialize the analytics engine"""
        self.products_df = None
        self.data_loaded = False
        
    def load_data(self, products_df: pd.DataFrame):
        """Load product data for analysis"""
        try:
            self.products_df = products_df.copy()
            self._preprocess_data()
            self.data_loaded = True
            logger.info(f"Analytics engine loaded {len(self.products_df)} products")
        except Exception as e:
            logger.error(f"Error loading data in analytics engine: {e}")
            self.data_loaded = False
    
    def _preprocess_data(self):
        """Preprocess data for analysis"""
        if self.products_df is None:
            return
        
        # Clean price data
        self.products_df['price_clean'] = pd.to_numeric(
            self.products_df['price_num'], errors='coerce'
        )
        
        # Extract categories
        self.products_df['categories_list'] = self.products_df['categories_clean'].apply(
            self._extract_categories
        )
        
        # Create price ranges
        self.products_df['price_range'] = self._create_price_ranges()
        
        # Clean materials
        self.products_df['material_clean'] = (
            self.products_df['material_norm']
            .fillna('Unknown')
            .str.title()
        )
        
        # Clean brands
        self.products_df['brand_clean'] = (
            self.products_df['brand_norm']
            .fillna('Unknown')
            .str.title()
        )
    
    def _extract_categories(self, categories_str) -> List[str]:
        """Extract categories from string representation"""
        if pd.isna(categories_str) or not categories_str:
            return ['Uncategorized']
        
        try:
            # Try to parse as JSON
            if isinstance(categories_str, str):
                categories = json.loads(categories_str.replace("'", '"'))
                if isinstance(categories, list):
                    return [cat.title() for cat in categories if cat]
                else:
                    return [str(categories).title()]
            return [str(categories_str).title()]
        except:
            # If parsing fails, treat as single category
            return [str(categories_str).title()]
    
    def _create_price_ranges(self) -> pd.Series:
        """Create price range categories"""
        def categorize_price(price):
            if pd.isna(price):
                return 'Unknown'
            elif price < 50:
                return 'Under $50'
            elif price < 100:
                return '$50 - $100'
            elif price < 200:
                return '$100 - $200'
            elif price < 500:
                return '$200 - $500'
            elif price < 1000:
                return '$500 - $1000'
            else:
                return 'Over $1000'
        
        return self.products_df['price_clean'].apply(categorize_price)
    
    def get_overview(self) -> Dict[str, Any]:
        """Get general overview statistics"""
        if not self.data_loaded:
            return {"error": "Data not loaded"}
        
        try:
            overview = {
                "total_products": len(self.products_df),
                "average_price": float(self.products_df['price_clean'].mean()) if not self.products_df['price_clean'].isna().all() else 0,
                "median_price": float(self.products_df['price_clean'].median()) if not self.products_df['price_clean'].isna().all() else 0,
                "min_price": float(self.products_df['price_clean'].min()) if not self.products_df['price_clean'].isna().all() else 0,
                "max_price": float(self.products_df['price_clean'].max()) if not self.products_df['price_clean'].isna().all() else 0,
                "total_categories": len(set([cat for cats in self.products_df['categories_list'] for cat in cats])),
                "total_brands": self.products_df['brand_clean'].nunique(),
                "total_materials": self.products_df['material_clean'].nunique(),
                "products_with_images": int(self.products_df['images_clean'].notna().sum()),
                "products_with_descriptions": int(self.products_df['description'].notna().sum()),
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"Error generating overview: {e}")
            return {"error": str(e)}
    
    def get_price_distribution(self) -> Dict[str, Any]:
        """Get price distribution data"""
        if not self.data_loaded:
            return {"error": "Data not loaded"}
        
        try:
            # Price range distribution
            price_range_counts = self.products_df['price_range'].value_counts()
            
            # Price histogram data
            price_data = self.products_df['price_clean'].dropna()
            
            # Create price bins
            bins = [0, 25, 50, 100, 200, 500, 1000, price_data.max() + 1]
            bin_labels = ['$0-25', '$25-50', '$50-100', '$100-200', '$200-500', '$500-1000', '$1000+']
            
            price_histogram = pd.cut(price_data, bins=bins, labels=bin_labels, include_lowest=True)
            histogram_counts = price_histogram.value_counts()
            
            return {
                "price_ranges": {
                    "labels": price_range_counts.index.tolist(),
                    "values": price_range_counts.values.tolist()
                },
                "histogram": {
                    "labels": histogram_counts.index.tolist(),
                    "values": histogram_counts.values.tolist()
                },
                "statistics": {
                    "mean": float(price_data.mean()),
                    "median": float(price_data.median()),
                    "std": float(price_data.std()),
                    "min": float(price_data.min()),
                    "max": float(price_data.max())
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating price distribution: {e}")
            return {"error": str(e)}
    
    def get_category_stats(self) -> Dict[str, Any]:
        """Get category-based statistics"""
        if not self.data_loaded:
            return {"error": "Data not loaded"}
        
        try:
            # Flatten categories
            all_categories = []
            for cats in self.products_df['categories_list']:
                all_categories.extend(cats)
            
            category_counts = pd.Series(all_categories).value_counts()
            
            # Category price analysis
            category_prices = []
            for category in category_counts.head(10).index:
                category_products = self.products_df[
                    self.products_df['categories_list'].apply(lambda x: category in x)
                ]
                category_price_data = category_products['price_clean'].dropna()
                
                if not category_price_data.empty:
                    category_prices.append({
                        "category": category,
                        "count": len(category_products),
                        "avg_price": float(category_price_data.mean()),
                        "median_price": float(category_price_data.median()),
                        "min_price": float(category_price_data.min()),
                        "max_price": float(category_price_data.max())
                    })
            
            return {
                "category_counts": {
                    "labels": category_counts.head(15).index.tolist(),
                    "values": category_counts.head(15).values.tolist()
                },
                "category_prices": category_prices,
                "total_categories": len(category_counts)
            }
            
        except Exception as e:
            logger.error(f"Error generating category stats: {e}")
            return {"error": str(e)}
    
    def get_brand_analysis(self) -> Dict[str, Any]:
        """Get brand analysis"""
        if not self.data_loaded:
            return {"error": "Data not loaded"}
        
        try:
            brand_counts = self.products_df['brand_clean'].value_counts()
            
            # Brand price analysis
            brand_prices = []
            for brand in brand_counts.head(10).index:
                if brand != 'Unknown':
                    brand_products = self.products_df[self.products_df['brand_clean'] == brand]
                    brand_price_data = brand_products['price_clean'].dropna()
                    
                    if not brand_price_data.empty:
                        brand_prices.append({
                            "brand": brand,
                            "count": len(brand_products),
                            "avg_price": float(brand_price_data.mean()),
                            "median_price": float(brand_price_data.median()),
                            "price_range": f"${brand_price_data.min():.0f} - ${brand_price_data.max():.0f}"
                        })
            
            return {
                "brand_counts": {
                    "labels": brand_counts.head(15).index.tolist(),
                    "values": brand_counts.head(15).values.tolist()
                },
                "brand_prices": brand_prices,
                "total_brands": len(brand_counts)
            }
            
        except Exception as e:
            logger.error(f"Error generating brand analysis: {e}")
            return {"error": str(e)}
    
    def get_material_analysis(self) -> Dict[str, Any]:
        """Get material analysis"""
        if not self.data_loaded:
            return {"error": "Data not loaded"}
        
        try:
            material_counts = self.products_df['material_clean'].value_counts()
            
            # Material price analysis
            material_prices = []
            for material in material_counts.head(10).index:
                if material != 'Unknown':
                    material_products = self.products_df[self.products_df['material_clean'] == material]
                    material_price_data = material_products['price_clean'].dropna()
                    
                    if not material_price_data.empty:
                        material_prices.append({
                            "material": material,
                            "count": len(material_products),
                            "avg_price": float(material_price_data.mean()),
                            "median_price": float(material_price_data.median()),
                            "price_range": f"${material_price_data.min():.0f} - ${material_price_data.max():.0f}"
                        })
            
            return {
                "material_counts": {
                    "labels": material_counts.head(10).index.tolist(),
                    "values": material_counts.head(10).values.tolist()
                },
                "material_prices": material_prices,
                "total_materials": len(material_counts)
            }
            
        except Exception as e:
            logger.error(f"Error generating material analysis: {e}")
            return {"error": str(e)}
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Get data quality analysis"""
        if not self.data_loaded:
            return {"error": "Data not loaded"}
        
        try:
            total_products = len(self.products_df)
            
            # Check for missing data
            missing_data = {}
            important_columns = ['title', 'price_num', 'description', 'categories_clean', 
                               'material_norm', 'brand_norm', 'images_clean']
            
            for col in important_columns:
                if col in self.products_df.columns:
                    missing_count = self.products_df[col].isna().sum()
                    missing_data[col] = {
                        "missing_count": int(missing_count),
                        "missing_percentage": float(missing_count / total_products * 100),
                        "present_count": int(total_products - missing_count),
                        "present_percentage": float((total_products - missing_count) / total_products * 100)
                    }
            
            # Price data quality
            price_quality = {}
            if 'price_num' in self.products_df.columns:
                price_data = self.products_df['price_num']
                valid_prices = price_data.dropna()
                zero_prices = (valid_prices == 0).sum()
                negative_prices = (valid_prices < 0).sum()
                
                price_quality = {
                    "total_products": total_products,
                    "valid_prices": len(valid_prices),
                    "zero_prices": int(zero_prices),
                    "negative_prices": int(negative_prices),
                    "reasonable_prices": int(len(valid_prices[(valid_prices > 0) & (valid_prices < 10000)]))
                }
            
            return {
                "total_products": total_products,
                "missing_data": missing_data,
                "price_quality": price_quality,
                "completeness_score": float(
                    sum(data["present_percentage"] for data in missing_data.values()) / len(missing_data)
                ) if missing_data else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating data quality report: {e}")
            return {"error": str(e)}
    
    def get_search_insights(self, search_queries: List[str] = None) -> Dict[str, Any]:
        """Get insights about search patterns and product discoverability"""
        if not self.data_loaded:
            return {"error": "Data not loaded"}
        
        try:
            # Analyze product titles for common keywords
            all_titles = ' '.join(self.products_df['title'].fillna('').astype(str))
            
            # Simple keyword extraction (would be better with NLP)
            words = all_titles.lower().split()
            word_freq = pd.Series(words).value_counts()
            
            # Filter out common stop words
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
            filtered_words = word_freq[~word_freq.index.isin(stop_words)]
            
            return {
                "popular_keywords": {
                    "labels": filtered_words.head(20).index.tolist(),
                    "values": filtered_words.head(20).values.tolist()
                },
                "total_unique_words": len(filtered_words),
                "avg_title_length": float(self.products_df['title'].fillna('').str.len().mean()),
                "products_without_description": int(self.products_df['description'].isna().sum())
            }
            
        except Exception as e:
            logger.error(f"Error generating search insights: {e}")
            return {"error": str(e)}
    
    def generate_business_recommendations(self) -> Dict[str, Any]:
        """Generate business recommendations based on data analysis"""
        if not self.data_loaded:
            return {"error": "Data not loaded"}
        
        try:
            recommendations = []
            
            # Price-based recommendations
            price_data = self.products_df['price_clean'].dropna()
            if not price_data.empty:
                median_price = price_data.median()
                expensive_products = len(price_data[price_data > median_price * 2])
                
                if expensive_products > len(price_data) * 0.3:
                    recommendations.append({
                        "type": "pricing",
                        "priority": "medium",
                        "title": "High-End Product Focus",
                        "description": f"30%+ of products are priced above 2x median (${median_price:.0f}). Consider diversifying with mid-range options."
                    })
            
            # Category-based recommendations
            all_categories = []
            for cats in self.products_df['categories_list']:
                all_categories.extend(cats)
            
            category_counts = pd.Series(all_categories).value_counts()
            if len(category_counts) > 0:
                dominant_category = category_counts.iloc[0]
                if dominant_category > len(self.products_df) * 0.5:
                    recommendations.append({
                        "type": "inventory",
                        "priority": "high",
                        "title": "Category Diversification",
                        "description": f"Over 50% of products are in '{category_counts.index[0]}'. Consider expanding other categories."
                    })
            
            # Data quality recommendations
            missing_descriptions = self.products_df['description'].isna().sum()
            if missing_descriptions > len(self.products_df) * 0.2:
                recommendations.append({
                    "type": "data_quality",
                    "priority": "high",
                    "title": "Improve Product Descriptions",
                    "description": f"{missing_descriptions} products ({missing_descriptions/len(self.products_df)*100:.1f}%) lack descriptions. This hurts SEO and conversions."
                })
            
            missing_images = self.products_df['images_clean'].isna().sum()
            if missing_images > len(self.products_df) * 0.1:
                recommendations.append({
                    "type": "data_quality",
                    "priority": "high",
                    "title": "Add Product Images",
                    "description": f"{missing_images} products lack images. Visual content is crucial for e-commerce."
                })
            
            return {
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating business recommendations: {e}")
            return {"error": str(e)}