import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import json
import logging
from typing import List, Dict, Any, Optional
import asyncio
import os

logger = logging.getLogger(__name__)

class ProductRecommender:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the product recommender
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.products_df = None
        self.embeddings = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
    async def initialize(self):
        """Initialize the recommender with data and model"""
        try:
            # Load the sentence transformer model
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Load product data
            await self._load_data()
            
            # Generate embeddings if they don't exist
            await self._load_or_generate_embeddings()
            
            # Initialize TF-IDF for fallback search
            self._initialize_tfidf()
            
            logger.info("Product recommender initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing recommender: {e}")
            raise
    
    async def _load_data(self):
        """Load product data from CSV"""
        try:
            self.products_df = pd.read_csv("data/clean_products.csv")
            logger.info(f"Loaded {len(self.products_df)} products")
            
            # Create combined text for embedding
            self.products_df['combined_text'] = self._create_combined_text()
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def _create_combined_text(self) -> pd.Series:
        """Create combined text from product features for embedding"""
        def combine_features(row):
            parts = []
            
            # Title (most important)
            if pd.notna(row.get('title')):
                parts.append(str(row['title']))
            
            # Description
            if pd.notna(row.get('description')):
                parts.append(str(row['description']))
            
            # Categories
            if pd.notna(row.get('categories_clean')):
                try:
                    categories = json.loads(str(row['categories_clean']).replace("'", '"'))
                    if isinstance(categories, list):
                        parts.extend(categories)
                    else:
                        parts.append(str(categories))
                except:
                    parts.append(str(row['categories_clean']))
            
            # Material
            if pd.notna(row.get('material_norm')):
                parts.append(f"material: {row['material_norm']}")
            
            # Brand
            if pd.notna(row.get('brand_norm')):
                parts.append(f"brand: {row['brand_norm']}")
            
            # Color
            if pd.notna(row.get('color_norm')):
                parts.append(f"color: {row['color_norm']}")
            
            return ' '.join(parts)
        
        return self.products_df.apply(combine_features, axis=1)
    
    async def _load_or_generate_embeddings(self):
        """Load existing embeddings or generate new ones"""
        embeddings_path = "data/product_embeddings.pkl"
        
        if os.path.exists(embeddings_path):
            try:
                logger.info("Loading existing embeddings...")
                with open(embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
                logger.info(f"Loaded embeddings with shape: {self.embeddings.shape}")
                return
            except Exception as e:
                logger.warning(f"Error loading embeddings: {e}. Generating new ones...")
        
        # Generate new embeddings
        logger.info("Generating product embeddings...")
        texts = self.products_df['combined_text'].tolist()
        
        # Generate embeddings in batches for memory efficiency
        batch_size = 100
        embeddings_list = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch, convert_to_tensor=False)
            embeddings_list.append(batch_embeddings)
            logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        self.embeddings = np.vstack(embeddings_list)
        
        # Save embeddings
        try:
            with open(embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings, f)
            logger.info(f"Saved embeddings to {embeddings_path}")
        except Exception as e:
            logger.warning(f"Could not save embeddings: {e}")
    
    def _initialize_tfidf(self):
        """Initialize TF-IDF vectorizer for fallback search"""
        try:
            texts = self.products_df['combined_text'].fillna('').tolist()
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            logger.info("TF-IDF vectorizer initialized")
        except Exception as e:
            logger.error(f"Error initializing TF-IDF: {e}")
    
    async def get_recommendations(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get product recommendations based on a query
        
        Args:
            query: Search query
            top_k: Number of recommendations to return
            
        Returns:
            List of recommended products with similarity scores
        """
        try:
            if self.model is None or self.embeddings is None:
                return await self._fallback_search(query, top_k)
            
            # Generate query embedding
            query_embedding = self.model.encode([query], convert_to_tensor=False)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top-k similar products
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            recommendations = []
            for idx in top_indices:
                product = self.products_df.iloc[idx].to_dict()
                product['similarity_score'] = float(similarities[idx])
                
                # Clean up the product data
                product = self._clean_product_data(product)
                recommendations.append(product)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return await self._fallback_search(query, top_k)
    
    async def get_similar_products(self, product_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get products similar to a given product
        
        Args:
            product_id: ID of the reference product
            top_k: Number of similar products to return
            
        Returns:
            List of similar products with similarity scores
        """
        try:
            # Find the product
            product_row = self.products_df[self.products_df['uniq_id'] == product_id]
            if product_row.empty:
                logger.warning(f"Product {product_id} not found")
                return []
            
            product_idx = product_row.index[0]
            
            if self.embeddings is None:
                return []
            
            # Get product embedding
            product_embedding = self.embeddings[product_idx:product_idx+1]
            
            # Calculate similarities with all products
            similarities = cosine_similarity(product_embedding, self.embeddings)[0]
            
            # Get top-k similar products (excluding the product itself)
            top_indices = np.argsort(similarities)[::-1][1:top_k+1]  # Skip first (itself)
            
            similar_products = []
            for idx in top_indices:
                product = self.products_df.iloc[idx].to_dict()
                product['similarity_score'] = float(similarities[idx])
                
                # Clean up the product data
                product = self._clean_product_data(product)
                similar_products.append(product)
            
            return similar_products
            
        except Exception as e:
            logger.error(f"Error getting similar products: {e}")
            return []
    
    async def _fallback_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Fallback search using TF-IDF when embeddings are not available"""
        try:
            if self.tfidf_vectorizer is None or self.tfidf_matrix is None:
                return self._simple_text_search(query, top_k)
            
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Get top-k similar products
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            recommendations = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include products with some similarity
                    product = self.products_df.iloc[idx].to_dict()
                    product['similarity_score'] = float(similarities[idx])
                    
                    # Clean up the product data
                    product = self._clean_product_data(product)
                    recommendations.append(product)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in fallback search: {e}")
            return self._simple_text_search(query, top_k)
    
    def _simple_text_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Simple text search as last resort"""
        try:
            query_lower = query.lower()
            matched_products = []
            
            for idx, row in self.products_df.iterrows():
                score = 0
                
                # Check title
                if pd.notna(row.get('title')) and query_lower in str(row['title']).lower():
                    score += 3
                
                # Check description
                if pd.notna(row.get('description')) and query_lower in str(row['description']).lower():
                    score += 2
                
                # Check categories
                if pd.notna(row.get('categories_clean')) and query_lower in str(row['categories_clean']).lower():
                    score += 2
                
                # Check material
                if pd.notna(row.get('material_norm')) and query_lower in str(row['material_norm']).lower():
                    score += 1
                
                # Check brand
                if pd.notna(row.get('brand_norm')) and query_lower in str(row['brand_norm']).lower():
                    score += 1
                
                if score > 0:
                    product = row.to_dict()
                    product['similarity_score'] = score / 10.0  # Normalize score
                    product = self._clean_product_data(product)
                    matched_products.append(product)
            
            # Sort by score and return top-k
            matched_products.sort(key=lambda x: x['similarity_score'], reverse=True)
            return matched_products[:top_k]
            
        except Exception as e:
            logger.error(f"Error in simple text search: {e}")
            return []
    
    def _clean_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and format product data for API response"""
        # Replace NaN values with appropriate defaults
        for key, value in product.items():
            if pd.isna(value):
                product[key] = None
            elif isinstance(value, (np.int64, np.float64)):
                product[key] = float(value) if not np.isnan(value) else None
        
        # Ensure required fields exist
        if 'uniq_id' not in product or product['uniq_id'] is None:
            product['uniq_id'] = f"product_{hash(str(product))}"
        
        if 'price_num' in product and product['price_num'] is not None:
            try:
                product['price_num'] = float(product['price_num'])
            except (ValueError, TypeError):
                product['price_num'] = 0.0
        
        # Remove the combined_text field from API response
        if 'combined_text' in product:
            del product['combined_text']
        
        return product
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recommender statistics"""
        return {
            "total_products": len(self.products_df) if self.products_df is not None else 0,
            "embeddings_shape": self.embeddings.shape if self.embeddings is not None else None,
            "model_name": self.model_name,
            "tfidf_features": self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else None
        }