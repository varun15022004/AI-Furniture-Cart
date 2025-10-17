"""
Advanced AI Engine for Furniture E-commerce Platform
Features:
- AI-based recommendation system with personalization
- Generative AI for product descriptions
- Computer Vision for image recognition
- Vector Database for semantic search
- Machine Learning for user behavior analysis
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import openai
import os
import logging
import json
import requests
from typing import List, Dict, Any, Optional
import pickle
from datetime import datetime, timedelta
import sqlite3
from sentence_transformers import SentenceTransformer
import cv2
from PIL import Image
import torch
import io

logger = logging.getLogger(__name__)

class VectorDatabase:
    """Simple vector database using SQLite for embeddings storage"""
    
    def __init__(self, db_path="vector_db.sqlite"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the vector database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for storing embeddings and metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_embeddings (
                id TEXT PRIMARY KEY,
                embedding BLOB,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                user_id TEXT,
                product_id TEXT,
                interaction_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_embedding(self, item_id: str, embedding: np.ndarray, metadata: Dict):
        """Store embedding with metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        embedding_blob = pickle.dumps(embedding)
        metadata_json = json.dumps(metadata)
        
        cursor.execute('''
            INSERT OR REPLACE INTO product_embeddings (id, embedding, metadata)
            VALUES (?, ?, ?)
        ''', (item_id, embedding_blob, metadata_json))
        
        conn.commit()
        conn.close()
    
    def get_embedding(self, item_id: str):
        """Retrieve embedding by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT embedding, metadata FROM product_embeddings WHERE id = ?', (item_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            embedding = pickle.loads(result[0])
            metadata = json.loads(result[1])
            return embedding, metadata
        return None, None
    
    def similarity_search(self, query_embedding: np.ndarray, top_k: int = 10):
        """Perform similarity search"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, embedding, metadata FROM product_embeddings')
        results = cursor.fetchall()
        
        conn.close()
        
        similarities = []
        for item_id, embedding_blob, metadata in results:
            embedding = pickle.loads(embedding_blob)
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            similarities.append((item_id, similarity, json.loads(metadata)))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

class ComputerVisionProcessor:
    """Computer Vision for image analysis and categorization"""
    
    def __init__(self):
        self.feature_extractor = None
        self.furniture_categories = [
            'chair', 'sofa', 'table', 'bed', 'desk', 'cabinet', 'shelf', 'lamp', 
            'ottoman', 'bench', 'dresser', 'nightstand', 'bookshelf', 'wardrobe'
        ]
    
    def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """Analyze furniture image and extract features"""
        try:
            # Download and process image
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return {"error": "Failed to download image"}
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(response.content))
            
            # Basic image analysis
            analysis = {
                "dominant_colors": self.extract_dominant_colors(image),
                "predicted_category": self.predict_category_simple(image_url),
                "image_quality": self.assess_image_quality(image),
                "style_features": self.extract_style_features(image),
                "dimensions": image.size
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing image {image_url}: {e}")
            return {"error": str(e)}
    
    def extract_dominant_colors(self, image: Image.Image, k: int = 5) -> List[str]:
        """Extract dominant colors from image"""
        try:
            # Convert to RGB and resize for processing
            image = image.convert('RGB').resize((150, 150))
            pixels = np.array(image).reshape(-1, 3)
            
            # Use KMeans to find dominant colors
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = []
            for center in kmeans.cluster_centers_:
                hex_color = '#{:02x}{:02x}{:02x}'.format(int(center[0]), int(center[1]), int(center[2]))
                colors.append(hex_color)
            
            return colors
        except Exception as e:
            logger.error(f"Error extracting colors: {e}")
            return []
    
    def predict_category_simple(self, image_url: str) -> str:
        """Simple category prediction based on URL and basic analysis"""
        # Simple heuristic-based categorization
        url_lower = image_url.lower()
        for category in self.furniture_categories:
            if category in url_lower:
                return category
        
        return "furniture"
    
    def assess_image_quality(self, image: Image.Image) -> Dict[str, float]:
        """Assess image quality metrics"""
        try:
            # Convert to numpy array
            img_array = np.array(image.convert('L'))  # Convert to grayscale
            
            # Calculate basic quality metrics
            sharpness = self.calculate_sharpness(img_array)
            brightness = np.mean(img_array) / 255.0
            contrast = np.std(img_array) / 255.0
            
            return {
                "sharpness": float(sharpness),
                "brightness": float(brightness),
                "contrast": float(contrast),
                "overall_quality": float((sharpness + contrast) / 2)
            }
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return {"overall_quality": 0.5}
    
    def calculate_sharpness(self, image_array: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        try:
            # Apply Laplacian filter
            laplacian_var = cv2.Laplacian(image_array, cv2.CV_64F).var()
            # Normalize to 0-1 range
            return min(laplacian_var / 1000, 1.0)
        except:
            return 0.5
    
    def extract_style_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract style-related features"""
        try:
            # Basic style analysis based on color and composition
            colors = self.extract_dominant_colors(image, 3)
            
            # Determine style characteristics
            style_features = {
                "color_palette": colors,
                "style_prediction": self.predict_style_from_colors(colors),
                "complexity": self.assess_visual_complexity(image)
            }
            
            return style_features
        except Exception as e:
            logger.error(f"Error extracting style features: {e}")
            return {}
    
    def predict_style_from_colors(self, colors: List[str]) -> str:
        """Predict furniture style based on color palette"""
        # Simple heuristic-based style prediction
        color_styles = {
            "modern": ["#000000", "#ffffff", "#808080"],
            "rustic": ["#8B4513", "#D2B48C", "#DEB887"],
            "vintage": ["#800080", "#008080", "#F0E68C"],
            "industrial": ["#2F4F4F", "#696969", "#A9A9A9"],
            "scandinavian": ["#F5F5DC", "#FFFAF0", "#E6E6FA"]
        }
        
        # Calculate similarity to known style palettes
        best_style = "contemporary"
        best_score = 0
        
        for style, style_colors in color_styles.items():
            score = self.calculate_color_similarity(colors, style_colors)
            if score > best_score:
                best_score = score
                best_style = style
        
        return best_style
    
    def calculate_color_similarity(self, colors1: List[str], colors2: List[str]) -> float:
        """Calculate similarity between two color palettes"""
        # Simple color similarity based on hex values
        similarity = 0.0
        for color1 in colors1[:3]:  # Use top 3 colors
            for color2 in colors2:
                # Convert hex to RGB and calculate similarity
                rgb1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
                rgb2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
                
                # Calculate Euclidean distance in RGB space
                distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))
                similarity += max(0, 1 - distance / 441.67)  # Max distance in RGB
        
        return similarity / (len(colors1) * len(colors2))
    
    def assess_visual_complexity(self, image: Image.Image) -> float:
        """Assess visual complexity of the image"""
        try:
            # Convert to grayscale
            gray = np.array(image.convert('L'))
            
            # Calculate edge density as complexity measure
            edges = cv2.Canny(gray, 50, 150)
            complexity = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            return float(complexity)
        except:
            return 0.5

class GenerativeAIDescriptor:
    """Generative AI for creating product descriptions"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        self.style_templates = {
            "modern": "sleek, contemporary design with clean lines and minimalist aesthetics",
            "rustic": "warm, natural materials with authentic craftsmanship and timeless appeal",
            "vintage": "classic elegance with rich history and distinctive character",
            "industrial": "raw, urban-inspired design with metal accents and bold functionality",
            "scandinavian": "Nordic simplicity featuring light woods and cozy, functional design"
        }
    
    def generate_description(self, product_data: Dict[str, Any], 
                           image_analysis: Optional[Dict] = None,
                           target_audience: str = "general") -> str:
        """Generate creative product description using AI"""
        
        # Try OpenAI API first, fall back to template-based generation
        if self.api_key and self.api_key != "your_openai_api_key_here":
            try:
                return self._generate_with_openai(product_data, image_analysis, target_audience)
            except Exception as e:
                logger.warning(f"OpenAI API failed, using template generation: {e}")
        
        return self._generate_with_template(product_data, image_analysis, target_audience)
    
    def _generate_with_openai(self, product_data: Dict, 
                             image_analysis: Optional[Dict],
                             target_audience: str) -> str:
        """Generate description using OpenAI API"""
        
        # Prepare context
        context = f"""
        Product: {product_data.get('title', 'Furniture Item')}
        Category: {product_data.get('category', 'furniture')}
        Material: {product_data.get('material', 'premium materials')}
        Brand: {product_data.get('brand', 'quality manufacturer')}
        Price Range: {product_data.get('price_range', 'affordable luxury')}
        """
        
        if image_analysis:
            style = image_analysis.get('style_features', {}).get('style_prediction', 'contemporary')
            colors = image_analysis.get('dominant_colors', [])
            context += f"\nStyle: {style}\nColor Palette: {', '.join(colors[:3])}"
        
        audience_tone = {
            "luxury": "sophisticated and exclusive",
            "family": "practical and family-friendly",
            "young_professional": "modern and stylish",
            "general": "appealing and versatile"
        }
        
        prompt = f"""
        Create an engaging, creative product description for this furniture item.
        Make it {audience_tone.get(target_audience, 'appealing and versatile')}.
        
        Context: {context}
        
        Requirements:
        - 2-3 sentences maximum
        - Highlight key features and benefits
        - Use emotional and sensory language
        - Include style and quality aspects
        - Make it compelling for online shoppers
        
        Description:
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_with_template(self, product_data: Dict,
                               image_analysis: Optional[Dict],
                               target_audience: str) -> str:
        """Generate description using templates as fallback"""
        
        title = product_data.get('title', 'Premium Furniture Piece')
        category = product_data.get('category', 'furniture')
        material = product_data.get('material', 'high-quality materials')
        brand = product_data.get('brand', '')
        
        # Determine style from image analysis or default
        style = "contemporary"
        if image_analysis and 'style_features' in image_analysis:
            style = image_analysis['style_features'].get('style_prediction', 'contemporary')
        
        style_desc = self.style_templates.get(style, "modern design with exceptional craftsmanship")
        
        # Generate based on audience
        if target_audience == "luxury":
            description = f"Indulge in the sophisticated elegance of this {title.lower()}. "
            description += f"Featuring {style_desc}, this {category} exemplifies luxury living. "
            description += f"Crafted from {material} with meticulous attention to detail."
        
        elif target_audience == "family":
            description = f"Transform your home with this versatile {title.lower()}. "
            description += f"Combining {style_desc} with family-friendly functionality, "
            description += f"this {category} is built from durable {material} to withstand daily life while maintaining its beauty."
        
        elif target_audience == "young_professional":
            description = f"Elevate your space with this stunning {title.lower()}. "
            description += f"Perfect for the modern lifestyle, featuring {style_desc} "
            description += f"and premium {material} construction that makes a statement in any room."
        
        else:  # general
            description = f"Discover the perfect blend of style and comfort with this {title.lower()}. "
            description += f"Showcasing {style_desc}, this {category} is expertly crafted from {material}. "
            description += f"An ideal addition to elevate any living space with timeless appeal."
        
        if brand and brand.strip():
            description += f" From {brand}, a name synonymous with quality and innovation."
        
        return description

class PersonalizedRecommendationEngine:
    """AI-powered personalized recommendation system"""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
        self.user_profiles = {}  # In-memory user profiles
        self.interaction_weights = {
            'view': 1.0,
            'add_to_cart': 3.0,
            'purchase': 5.0,
            'like': 2.0,
            'share': 1.5
        }
    
    def update_user_interaction(self, user_id: str, product_id: str, 
                               interaction_type: str, context: Dict = None):
        """Update user interaction history"""
        try:
            conn = sqlite3.connect(self.vector_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_interactions (user_id, product_id, interaction_type, context)
                VALUES (?, ?, ?, ?)
            ''', (user_id, product_id, interaction_type, json.dumps(context or {})))
            
            conn.commit()
            conn.close()
            
            # Update user profile
            self._update_user_profile(user_id, product_id, interaction_type)
            
        except Exception as e:
            logger.error(f"Error updating user interaction: {e}")
    
    def _update_user_profile(self, user_id: str, product_id: str, interaction_type: str):
        """Update user profile based on interaction"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preferences': {},
                'categories': {},
                'styles': {},
                'price_range': {'min': 0, 'max': 10000},
                'last_updated': datetime.now()
            }
        
        weight = self.interaction_weights.get(interaction_type, 1.0)
        
        # Get product embedding and metadata
        embedding, metadata = self.vector_db.get_embedding(product_id)
        if metadata:
            category = metadata.get('category', 'unknown')
            style = metadata.get('style', 'contemporary')
            price = metadata.get('price', 0)
            
            # Update category preferences
            if category in self.user_profiles[user_id]['categories']:
                self.user_profiles[user_id]['categories'][category] += weight
            else:
                self.user_profiles[user_id]['categories'][category] = weight
            
            # Update style preferences
            if style in self.user_profiles[user_id]['styles']:
                self.user_profiles[user_id]['styles'][style] += weight
            else:
                self.user_profiles[user_id]['styles'][style] = weight
            
            # Update price range
            profile = self.user_profiles[user_id]
            if price > 0:
                if price < profile['price_range']['min'] or profile['price_range']['min'] == 0:
                    profile['price_range']['min'] = price * 0.8
                if price > profile['price_range']['max']:
                    profile['price_range']['max'] = price * 1.2
    
    def get_personalized_recommendations(self, user_id: str, 
                                       exclude_products: List[str] = None,
                                       top_k: int = 10) -> List[Dict]:
        """Get personalized recommendations for user"""
        try:
            if user_id not in self.user_profiles:
                # Return popular/trending items for new users
                return self._get_popular_recommendations(top_k)
            
            profile = self.user_profiles[user_id]
            
            # Get user's preferred categories and styles
            top_categories = sorted(profile['categories'].items(), 
                                  key=lambda x: x[1], reverse=True)[:3]
            top_styles = sorted(profile['styles'].items(), 
                              key=lambda x: x[1], reverse=True)[:2]
            
            # Create user preference vector
            preference_text = " ".join([
                f"{cat} {cat} {cat}" * min(3, int(weight))  # Repeat based on weight
                for cat, weight in top_categories
            ])
            preference_text += " " + " ".join([
                f"{style} style {style} design" * min(2, int(weight))
                for style, weight in top_styles
            ])
            
            if preference_text.strip():
                user_embedding = self.model.encode([preference_text])[0]
                
                # Find similar products
                similar_products = self.vector_db.similarity_search(user_embedding, top_k * 2)
                
                # Filter and rank results
                recommendations = []
                exclude_set = set(exclude_products or [])
                
                for product_id, similarity, metadata in similar_products:
                    if product_id in exclude_set:
                        continue
                    
                    # Apply personalization scoring
                    personal_score = self._calculate_personalization_score(
                        metadata, profile, similarity)
                    
                    recommendations.append({
                        'product_id': product_id,
                        'similarity': similarity,
                        'personal_score': personal_score,
                        'metadata': metadata,
                        'reason': self._generate_recommendation_reason(metadata, profile)
                    })
                
                # Sort by personalized score and return top_k
                recommendations.sort(key=lambda x: x['personal_score'], reverse=True)
                return recommendations[:top_k]
            
            return self._get_popular_recommendations(top_k)
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            return self._get_popular_recommendations(top_k)
    
    def _calculate_personalization_score(self, metadata: Dict, 
                                       profile: Dict, similarity: float) -> float:
        """Calculate personalized score for a product"""
        score = similarity * 0.6  # Base similarity weight
        
        # Category preference boost
        category = metadata.get('category', '')
        if category in profile['categories']:
            category_weight = profile['categories'][category] / sum(profile['categories'].values())
            score += category_weight * 0.3
        
        # Style preference boost
        style = metadata.get('style', '')
        if style in profile['styles']:
            style_weight = profile['styles'][style] / sum(profile['styles'].values())
            score += style_weight * 0.2
        
        # Price range preference
        price = metadata.get('price', 0)
        if price > 0:
            price_range = profile['price_range']
            if price_range['min'] <= price <= price_range['max']:
                score += 0.1  # Small boost for price compatibility
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _generate_recommendation_reason(self, metadata: Dict, profile: Dict) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        category = metadata.get('category', '')
        if category in profile['categories']:
            reasons.append(f"matches your interest in {category}")
        
        style = metadata.get('style', '')
        if style in profile['styles']:
            reasons.append(f"fits your {style} style preference")
        
        if not reasons:
            reasons.append("recommended based on your browsing history")
        
        return reasons[0] if reasons else "popular choice"
    
    def _get_popular_recommendations(self, top_k: int) -> List[Dict]:
        """Get popular recommendations for new users"""
        # Simple fallback - would be replaced with actual popularity metrics
        try:
            conn = sqlite3.connect(self.vector_db.db_path)
            cursor = conn.cursor()
            
            # Get random products as popularity fallback
            cursor.execute('SELECT id, metadata FROM product_embeddings LIMIT ?', (top_k,))
            results = cursor.fetchall()
            
            conn.close()
            
            recommendations = []
            for product_id, metadata_json in results:
                metadata = json.loads(metadata_json)
                recommendations.append({
                    'product_id': product_id,
                    'similarity': 0.7,  # Default similarity
                    'personal_score': 0.7,
                    'metadata': metadata,
                    'reason': 'popular choice'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting popular recommendations: {e}")
            return []

class AdvancedAIEngine:
    """Main AI Engine coordinating all AI features"""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.cv_processor = ComputerVisionProcessor()
        self.ai_descriptor = GenerativeAIDescriptor()
        self.recommendation_engine = PersonalizedRecommendationEngine(self.vector_db)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        logger.info("Advanced AI Engine initialized")
    
    def process_product(self, product_data: Dict) -> Dict:
        """Process a product with all AI features"""
        try:
            product_id = product_data.get('uniq_id', str(product_data.get('id', '')))
            
            # Generate embeddings for semantic search
            text_content = self._prepare_text_for_embedding(product_data)
            embedding = self.model.encode([text_content])[0]
            
            # Analyze image if available
            image_analysis = None
            if product_data.get('images_clean'):
                try:
                    images = json.loads(product_data['images_clean'].replace("'", '"'))
                    if images and len(images) > 0:
                        image_analysis = self.cv_processor.analyze_image(images[0])
                except:
                    pass
            
            # Generate AI description
            ai_description = self.ai_descriptor.generate_description(
                product_data, image_analysis, "general"
            )
            
            # Prepare metadata for vector storage
            metadata = {
                'title': product_data.get('title', ''),
                'category': product_data.get('categories', 'furniture'),
                'material': product_data.get('material', ''),
                'brand': product_data.get('brand', ''),
                'price': float(product_data.get('price_num', 0)),
                'style': image_analysis.get('style_features', {}).get('style_prediction', 'contemporary') if image_analysis else 'contemporary',
                'ai_description': ai_description,
                'image_analysis': image_analysis
            }
            
            # Store in vector database
            self.vector_db.store_embedding(product_id, embedding, metadata)
            
            return {
                'product_id': product_id,
                'ai_description': ai_description,
                'image_analysis': image_analysis,
                'semantic_embedding': embedding.tolist(),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing product {product_data.get('uniq_id', 'unknown')}: {e}")
            return {'error': str(e)}
    
    def semantic_search(self, query: str, top_k: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform semantic search with optional filters"""
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Perform similarity search
            results = self.vector_db.similarity_search(query_embedding, top_k * 2)
            
            # Apply filters if provided
            if filters:
                filtered_results = []
                for product_id, similarity, metadata in results:
                    if self._matches_filters(metadata, filters):
                        filtered_results.append((product_id, similarity, metadata))
                results = filtered_results
            
            # Format results
            search_results = []
            for product_id, similarity, metadata in results[:top_k]:
                search_results.append({
                    'product_id': product_id,
                    'similarity_score': float(similarity),
                    'title': metadata.get('title', ''),
                    'category': metadata.get('category', ''),
                    'ai_description': metadata.get('ai_description', ''),
                    'style': metadata.get('style', ''),
                    'price': metadata.get('price', 0)
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def get_personalized_recommendations(self, user_id: str, context: Dict = None,
                                       top_k: int = 10) -> List[Dict]:
        """Get personalized recommendations with context"""
        return self.recommendation_engine.get_personalized_recommendations(
            user_id, context.get('exclude_products', []) if context else [], top_k
        )
    
    def update_user_interaction(self, user_id: str, product_id: str, 
                               interaction_type: str, context: Dict = None):
        """Update user interaction for personalization"""
        self.recommendation_engine.update_user_interaction(
            user_id, product_id, interaction_type, context
        )
    
    def _prepare_text_for_embedding(self, product_data: Dict) -> str:
        """Prepare product text for embedding generation"""
        text_parts = [
            product_data.get('title', ''),
            product_data.get('description', ''),
            product_data.get('categories', ''),
            product_data.get('material', ''),
            product_data.get('brand', ''),
            product_data.get('color', '')
        ]
        
        return ' '.join(filter(None, text_parts))
    
    def _matches_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Check if product metadata matches filters"""
        for filter_key, filter_value in filters.items():
            if filter_key in metadata:
                if isinstance(filter_value, list):
                    if metadata[filter_key] not in filter_value:
                        return False
                elif isinstance(filter_value, dict):
                    # Range filter (e.g., price)
                    value = metadata[filter_key]
                    if 'min' in filter_value and value < filter_value['min']:
                        return False
                    if 'max' in filter_value and value > filter_value['max']:
                        return False
                else:
                    if str(metadata[filter_key]).lower() != str(filter_value).lower():
                        return False
        return True
    
    def get_analytics_insights(self) -> Dict:
        """Get AI-powered analytics insights"""
        try:
            conn = sqlite3.connect(self.vector_db.db_path)
            cursor = conn.cursor()
            
            # Get interaction statistics
            cursor.execute('''
                SELECT interaction_type, COUNT(*) as count, 
                       COUNT(DISTINCT user_id) as unique_users
                FROM user_interactions 
                WHERE timestamp > datetime('now', '-7 days')
                GROUP BY interaction_type
            ''')
            
            interactions = cursor.fetchall()
            
            # Get popular categories
            cursor.execute('''
                SELECT metadata FROM product_embeddings
            ''')
            
            products = cursor.fetchall()
            conn.close()
            
            # Analyze categories
            category_counts = {}
            style_counts = {}
            
            for (metadata_json,) in products:
                metadata = json.loads(metadata_json)
                category = metadata.get('category', 'unknown')
                style = metadata.get('style', 'unknown')
                
                category_counts[category] = category_counts.get(category, 0) + 1
                style_counts[style] = style_counts.get(style, 0) + 1
            
            insights = {
                'user_interactions': [
                    {'type': interaction_type, 'count': count, 'unique_users': unique_users}
                    for interaction_type, count, unique_users in interactions
                ],
                'popular_categories': sorted(category_counts.items(), 
                                           key=lambda x: x[1], reverse=True)[:5],
                'trending_styles': sorted(style_counts.items(), 
                                        key=lambda x: x[1], reverse=True)[:5],
                'total_products_processed': len(products),
                'generated_at': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting analytics insights: {e}")
            return {'error': str(e)}