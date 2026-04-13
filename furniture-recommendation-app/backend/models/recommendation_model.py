import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict, Any, Optional

class RecommendationEngine:
    """
    Advanced recommendation engine using multiple ML techniques:
    1. Content-based filtering using TF-IDF and embeddings
    2. Semantic similarity using sentence transformers
    3. Hybrid recommendations combining multiple signals
    """
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self.sentence_model = None
        self.embeddings = None
        self.scaler = StandardScaler()
        
        # Load and prepare data
        self._load_data()
        self._prepare_features()
        self._initialize_models()
    
    def _load_data(self):
        """Load and preprocess the furniture dataset"""
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"Loaded {len(self.df)} products from dataset")
            
            # Clean and preprocess data
            self.df['combined_text'] = (
                self.df['title'].fillna('') + ' ' +
                self.df['description'].fillna('') + ' ' +
                self.df['categories'].fillna('') + ' ' +
                self.df['brand'].fillna('') + ' ' +
                self.df['material'].fillna('') + ' ' +
                self.df['color'].fillna('')
            )
            
            # Convert price to numeric
            self.df['price'] = pd.to_numeric(self.df['price'], errors='coerce')
            
            # Handle missing values
            self.df = self.df.fillna('')
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            # Create dummy data if file not found
            self._create_dummy_data()
    
    def _create_dummy_data(self):
        """Create dummy data for testing if dataset is not available"""
        dummy_data = {
            'uniq_id': range(1, 11),
            'title': [
                'Modern Oak Dining Table', 'Comfortable Office Chair', 'Minimalist Bookshelf',
                'Velvet Sofa Set', 'Rustic Coffee Table', 'Memory Foam Mattress',
                'Scandinavian Nightstand', 'Industrial Bar Stool', 'Outdoor Patio Set', 'Kids Study Desk'
            ],
            'brand': ['IKEA', 'Herman Miller', 'MUJI', 'West Elm', 'Pottery Barn', 'Casper', 'Article', 'CB2', 'IKEA', 'IKEA'],
            'description': [
                'A sleek dining table made from oak wood',
                'Ergonomic office chair with lumbar support',
                'Clean-lined bookshelf with adjustable shelves',
                'Luxurious velvet sofa with cushions',
                'Handcrafted coffee table with storage',
                'Premium memory foam mattress',
                'Sleek nightstand with drawer',
                'Adjustable bar stool with metal frame',
                'Weather-resistant patio furniture set',
                'Adjustable study desk for children'
            ],
            'price': [299.99, 459.00, 189.99, 1299.99, 549.00, 799.99, 149.99, 199.99, 399.99, 129.99],
            'categories': [
                'Dining Room > Dining Tables', 'Office > Chairs', 'Living Room > Storage',
                'Living Room > Sofas', 'Living Room > Coffee Tables', 'Bedroom > Mattresses',
                'Bedroom > Nightstands', 'Dining Room > Bar Stools', 'Outdoor > Patio Sets', 'Kids > Desks'
            ],
            'material': ['Oak Wood', 'Mesh/Plastic', 'Pine Wood', 'Velvet/Wood', 'Reclaimed Wood', 'Memory Foam', 'Oak Wood', 'Metal/Leather', 'Aluminum/Textilene', 'MDF/Steel'],
            'color': ['Natural Brown', 'Black', 'White', 'Navy Blue', 'Brown', 'White', 'Natural', 'Black', 'Gray', 'White/Pink']
        }
        
        self.df = pd.DataFrame(dummy_data)
        self.df['combined_text'] = (
            self.df['title'] + ' ' + self.df['description'] + ' ' +
            self.df['categories'] + ' ' + self.df['brand'] + ' ' +
            self.df['material'] + ' ' + self.df['color']
        )
        print("Created dummy dataset for testing")
    
    def _prepare_features(self):
        """Prepare features for recommendation algorithms"""
        # Create TF-IDF features
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['combined_text'])
        
        print(f"Created TF-IDF matrix with shape: {self.tfidf_matrix.shape}")
    
    def _initialize_models(self):
        """Initialize sentence transformer for semantic embeddings"""
        try:
            # Use a lightweight sentence transformer model
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate embeddings for all products
            print("Generating sentence embeddings...")
            self.embeddings = self.sentence_model.encode(self.df['combined_text'].tolist())
            print(f"Generated embeddings with shape: {self.embeddings.shape}")
            
        except Exception as e:
            print(f"Error initializing sentence transformer: {str(e)}")
            self.sentence_model = None
            self.embeddings = None
    
    def get_recommendations(self, query: str, max_results: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get product recommendations based on user query using hybrid approach
        """
        try:
            # Method 1: TF-IDF based similarity
            tfidf_scores = self._get_tfidf_recommendations(query, max_results * 2)
            
            # Method 2: Semantic similarity using sentence embeddings
            semantic_scores = self._get_semantic_recommendations(query, max_results * 2)
            
            # Method 3: Combine scores and apply filters
            combined_recommendations = self._combine_recommendations(
                tfidf_scores, semantic_scores, filters, max_results
            )
            
            return combined_recommendations
            
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return self._get_fallback_recommendations(max_results)
    
    def _get_tfidf_recommendations(self, query: str, max_results: int) -> List[tuple]:
        """Get recommendations using TF-IDF similarity"""
        # Transform query using fitted vectorizer
        query_vector = self.tfidf_vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top similar products
        top_indices = similarities.argsort()[-max_results:][::-1]
        
        return [(idx, similarities[idx]) for idx in top_indices if similarities[idx] > 0]
    
    def _get_semantic_recommendations(self, query: str, max_results: int) -> List[tuple]:
        """Get recommendations using semantic similarity"""
        if self.sentence_model is None or self.embeddings is None:
            return []
        
        try:
            # Encode query
            query_embedding = self.sentence_model.encode([query])
            
            # Calculate cosine similarity with all product embeddings
            similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
            
            # Get top similar products
            top_indices = similarities.argsort()[-max_results:][::-1]
            
            return [(idx, similarities[idx]) for idx in top_indices if similarities[idx] > 0]
            
        except Exception as e:
            print(f"Error in semantic recommendations: {str(e)}")
            return []
    
    def _combine_recommendations(self, tfidf_scores: List[tuple], semantic_scores: List[tuple], 
                               filters: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
        """Combine TF-IDF and semantic scores with hybrid weighting"""
        # Create score dictionary
        combined_scores = {}
        
        # Weight TF-IDF scores (40%)
        for idx, score in tfidf_scores:
            combined_scores[idx] = combined_scores.get(idx, 0) + 0.4 * score
        
        # Weight semantic scores (60%)
        for idx, score in semantic_scores:
            combined_scores[idx] = combined_scores.get(idx, 0) + 0.6 * score
        
        # Sort by combined score
        sorted_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Apply filters and convert to product dictionaries
        recommendations = []
        for idx, score in sorted_items[:max_results * 2]:  # Get more to account for filtering
            product = self._get_product_dict(idx, score)
            
            # Apply filters
            if self._apply_filters(product, filters):
                recommendations.append(product)
                
            if len(recommendations) >= max_results:
                break
        
        return recommendations[:max_results]
    
    def _apply_filters(self, product: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to product"""
        if not filters:
            return True
        
        try:
            # Price filters
            if 'min_price' in filters and product.get('price', 0) < filters['min_price']:
                return False
            if 'max_price' in filters and product.get('price', float('inf')) > filters['max_price']:
                return False
            
            # Category filter
            if 'categories' in filters and filters['categories'].lower() not in product.get('categories', '').lower():
                return False
            
            # Brand filter
            if 'brand' in filters and filters['brand'].lower() not in product.get('brand', '').lower():
                return False
            
            # Material filter
            if 'material' in filters and filters['material'].lower() not in product.get('material', '').lower():
                return False
            
            # Color filter
            if 'color' in filters and filters['color'].lower() not in product.get('color', '').lower():
                return False
            
            return True
            
        except Exception as e:
            print(f"Error applying filters: {str(e)}")
            return True
    
    def _get_product_dict(self, idx: int, score: float) -> Dict[str, Any]:
        """Convert dataframe row to product dictionary"""
        product = self.df.iloc[idx].to_dict()
        product['similarity_score'] = float(score)
        product['recommendation_rank'] = None  # Will be set later
        return product
    
    def get_similar_products(self, product_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get products similar to a specific product"""
        try:
            # Find the product
            product_row = self.df[self.df['uniq_id'].astype(str) == str(product_id)]
            if product_row.empty:
                return []
            
            product_idx = product_row.index[0]
            
            # Use the product's combined text as query
            query_text = self.df.iloc[product_idx]['combined_text']
            
            # Get recommendations but exclude the original product
            recommendations = self.get_recommendations(query_text, limit + 1)
            
            # Remove the original product from recommendations
            similar_products = [
                rec for rec in recommendations 
                if str(rec.get('uniq_id')) != str(product_id)
            ]
            
            return similar_products[:limit]
            
        except Exception as e:
            print(f"Error getting similar products: {str(e)}")
            return []
    
    def search_products(self, query: str, filters: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Search products with text query and filters"""
        return self.get_recommendations(query, limit, filters)
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID"""
        try:
            product_row = self.df[self.df['uniq_id'].astype(str) == str(product_id)]
            if product_row.empty:
                return None
            
            return product_row.iloc[0].to_dict()
            
        except Exception as e:
            print(f"Error getting product by ID: {str(e)}")
            return None
    
    def _get_fallback_recommendations(self, max_results: int) -> List[Dict[str, Any]]:
        """Fallback recommendations when other methods fail"""
        try:
            # Return top products by price or random selection
            sample_products = self.df.sample(min(max_results, len(self.df)))
            
            recommendations = []
            for _, product in sample_products.iterrows():
                product_dict = product.to_dict()
                product_dict['similarity_score'] = 0.5  # Default score
                recommendations.append(product_dict)
            
            return recommendations
            
        except Exception as e:
            print(f"Error in fallback recommendations: {str(e)}")
            return []
    
    def get_category_products(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get products from a specific category"""
        try:
            category_products = self.df[
                self.df['categories'].str.contains(category, case=False, na=False)
            ]
            
            # Sample or take top products
            if len(category_products) > limit:
                category_products = category_products.sample(limit)
            
            recommendations = []
            for _, product in category_products.iterrows():
                product_dict = product.to_dict()
                product_dict['similarity_score'] = 1.0
                recommendations.append(product_dict)
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting category products: {str(e)}")
            return []
    
    def get_trending_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending products (mock implementation)"""
        try:
            # For now, return products with highest prices as "trending"
            trending = self.df.nlargest(limit, 'price')
            
            recommendations = []
            for _, product in trending.iterrows():
                product_dict = product.to_dict()
                product_dict['similarity_score'] = 0.9
                recommendations.append(product_dict)
            
            return recommendations
            
        except Exception as e:
            print(f"Error getting trending products: {str(e)}")
            return []