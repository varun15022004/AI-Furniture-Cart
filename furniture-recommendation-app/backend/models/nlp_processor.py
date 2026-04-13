import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter

class NLPProcessor:
    """
    Advanced NLP processor for furniture product analysis:
    1. Query processing and intent recognition
    2. Product grouping based on semantic similarity
    3. Attribute extraction and classification
    4. Text preprocessing and feature extraction
    """
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.sentence_model = None
        self.stop_words = set()
        self.furniture_keywords = self._load_furniture_keywords()
        self.room_categories = self._load_room_categories()
        self.style_keywords = self._load_style_keywords()
        self.material_keywords = self._load_material_keywords()
        
        self._initialize_nltk()
        self._initialize_models()
    
    def _initialize_nltk(self):
        """Initialize NLTK resources"""
        try:
            # Download required NLTK data
            nltk_downloads = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
            for item in nltk_downloads:
                try:
                    nltk.data.find(f'tokenizers/{item}')
                except LookupError:
                    try:
                        nltk.download(item, quiet=True)
                    except:
                        pass
            
            self.stop_words = set(stopwords.words('english'))
            print("NLTK initialized successfully")
            
        except Exception as e:
            print(f"Warning: NLTK initialization failed: {str(e)}. Using fallback methods.")
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
    
    def _initialize_models(self):
        """Initialize sentence transformer model"""
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Sentence transformer model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {str(e)}")
            self.sentence_model = None
    
    def _load_furniture_keywords(self) -> Dict[str, List[str]]:
        """Load furniture-specific keywords for better understanding"""
        return {
            'seating': ['chair', 'sofa', 'couch', 'stool', 'bench', 'loveseat', 'armchair', 'recliner', 'ottoman'],
            'tables': ['table', 'desk', 'counter', 'island', 'surface', 'top'],
            'storage': ['shelf', 'cabinet', 'dresser', 'wardrobe', 'closet', 'chest', 'bookcase', 'storage'],
            'bedroom': ['bed', 'mattress', 'nightstand', 'headboard', 'frame', 'pillow'],
            'lighting': ['lamp', 'light', 'chandelier', 'sconce', 'fixture', 'pendant'],
            'decor': ['mirror', 'art', 'frame', 'vase', 'plant', 'decoration', 'ornament']
        }
    
    def _load_room_categories(self) -> Dict[str, List[str]]:
        """Load room-specific keywords"""
        return {
            'living_room': ['living room', 'lounge', 'family room', 'den', 'sitting area'],
            'bedroom': ['bedroom', 'master bedroom', 'guest room', 'sleep'],
            'dining_room': ['dining room', 'dining area', 'breakfast nook', 'eat'],
            'kitchen': ['kitchen', 'kitchenette', 'cook', 'culinary'],
            'office': ['office', 'study', 'work space', 'home office', 'desk area'],
            'bathroom': ['bathroom', 'bath', 'washroom', 'powder room'],
            'outdoor': ['outdoor', 'patio', 'garden', 'deck', 'balcony', 'terrace']
        }
    
    def _load_style_keywords(self) -> Dict[str, List[str]]:
        """Load style and aesthetic keywords"""
        return {
            'modern': ['modern', 'contemporary', 'sleek', 'minimalist', 'clean'],
            'traditional': ['traditional', 'classic', 'timeless', 'elegant', 'formal'],
            'rustic': ['rustic', 'farmhouse', 'country', 'cottage', 'vintage'],
            'industrial': ['industrial', 'urban', 'metal', 'concrete', 'loft'],
            'scandinavian': ['scandinavian', 'nordic', 'danish', 'hygge', 'cozy'],
            'mid_century': ['mid-century', 'retro', '50s', '60s', 'atomic']
        }
    
    def _load_material_keywords(self) -> Dict[str, List[str]]:
        """Load material-specific keywords"""
        return {
            'wood': ['wood', 'wooden', 'oak', 'pine', 'maple', 'cherry', 'mahogany', 'teak', 'bamboo'],
            'metal': ['metal', 'steel', 'aluminum', 'iron', 'brass', 'copper', 'chrome'],
            'fabric': ['fabric', 'cotton', 'linen', 'velvet', 'leather', 'suede', 'microfiber'],
            'glass': ['glass', 'crystal', 'transparent', 'clear'],
            'plastic': ['plastic', 'acrylic', 'polymer', 'resin']
        }
    
    def process_query(self, query: str) -> str:
        """
        Process user query to extract intent and improve search
        """
        try:
            # Clean and normalize the query
            processed_query = self._clean_text(query)
            
            # Extract furniture intent
            furniture_intent = self._extract_furniture_intent(processed_query)
            
            # Extract room context
            room_context = self._extract_room_context(processed_query)
            
            # Extract style preferences
            style_context = self._extract_style_context(processed_query)
            
            # Extract material preferences
            material_context = self._extract_material_context(processed_query)
            
            # Combine all context for enhanced query
            enhanced_query = self._build_enhanced_query(
                processed_query, furniture_intent, room_context, style_context, material_context
            )
            
            return enhanced_query
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return query.lower().strip()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\-]', '', text)
        
        return text
    
    def _extract_furniture_intent(self, query: str) -> List[str]:
        """Extract furniture type intent from query"""
        intents = []
        query_words = query.split()
        
        for category, keywords in self.furniture_keywords.items():
            for keyword in keywords:
                if keyword in query or any(word in keyword for word in query_words):
                    intents.append(category)
                    break
        
        return list(set(intents))
    
    def _extract_room_context(self, query: str) -> List[str]:
        """Extract room context from query"""
        contexts = []
        
        for room, keywords in self.room_categories.items():
            for keyword in keywords:
                if keyword in query:
                    contexts.append(room)
                    break
        
        return contexts
    
    def _extract_style_context(self, query: str) -> List[str]:
        """Extract style preferences from query"""
        styles = []
        
        for style, keywords in self.style_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    styles.append(style)
                    break
        
        return styles
    
    def _extract_material_context(self, query: str) -> List[str]:
        """Extract material preferences from query"""
        materials = []
        
        for material, keywords in self.material_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    materials.append(material)
                    break
        
        return materials
    
    def _build_enhanced_query(self, original_query: str, furniture_intent: List[str], 
                            room_context: List[str], style_context: List[str], 
                            material_context: List[str]) -> str:
        \"\"\"Build enhanced query with extracted context\"\"\"
        query_parts = [original_query]
        
        # Add furniture intent
        if furniture_intent:
            query_parts.extend(furniture_intent)
        
        # Add room context
        if room_context:
            query_parts.extend([ctx.replace('_', ' ') for ctx in room_context])
        
        # Add style context
        if style_context:
            query_parts.extend([style.replace('_', ' ') for style in style_context])
        
        # Add material context
        if material_context:
            query_parts.extend(material_context)
        
        # Combine and deduplicate
        enhanced_query = ' '.join(set(query_parts))
        
        return enhanced_query
    
    def group_similar_products(self, products_df: pd.DataFrame, num_clusters: int = 5) -> Dict[int, List[int]]:
        \"\"\"
        Group products into similar clusters using NLP techniques
        \"\"\"
        try:
            if len(products_df) < num_clusters:
                # If we have fewer products than clusters, each product is its own group
                return {i: [i] for i in range(len(products_df))}
            
            # Prepare text for clustering
            product_texts = []
            for _, product in products_df.iterrows():
                text = self._combine_product_text(product)
                product_texts.append(text)
            
            # Use sentence embeddings if available, otherwise TF-IDF
            if self.sentence_model:
                embeddings = self.sentence_model.encode(product_texts)
                
                # Perform k-means clustering
                kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(embeddings)
            else:
                # Fallback to TF-IDF clustering
                vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(product_texts)
                
                kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(tfidf_matrix.toarray())
            
            # Group products by cluster
            clusters = {}
            for idx, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(idx)
            
            return clusters
            
        except Exception as e:
            print(f\"Error in product grouping: {str(e)}\")
            # Return each product in its own group as fallback
            return {i: [i] for i in range(len(products_df))}
    
    def _combine_product_text(self, product: pd.Series) -> str:
        \"\"\"Combine product attributes into single text\"\"\"
        text_parts = []
        
        # Add title (most important)
        if pd.notna(product.get('title')):
            text_parts.append(str(product['title']))
        
        # Add description
        if pd.notna(product.get('description')):
            text_parts.append(str(product['description']))
        
        # Add category
        if pd.notna(product.get('categories')):
            text_parts.append(str(product['categories']))
        
        # Add brand
        if pd.notna(product.get('brand')):
            text_parts.append(str(product['brand']))
        
        # Add material
        if pd.notna(product.get('material')):
            text_parts.append(str(product['material']))
        
        # Add color
        if pd.notna(product.get('color')):
            text_parts.append(str(product['color']))
        
        return ' '.join(text_parts)
    
    def extract_product_attributes(self, product_text: str) -> Dict[str, Any]:
        \"\"\"
        Extract structured attributes from product text
        \"\"\"
        try:
            attributes = {
                'furniture_types': [],
                'rooms': [],
                'styles': [],
                'materials': [],
                'colors': [],
                'features': []
            }
            
            text_lower = product_text.lower()
            
            # Extract furniture types
            for category, keywords in self.furniture_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        attributes['furniture_types'].append(category)
                        break
            
            # Extract room associations
            for room, keywords in self.room_categories.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        attributes['rooms'].append(room)
                        break
            
            # Extract styles
            for style, keywords in self.style_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        attributes['styles'].append(style)
                        break
            
            # Extract materials
            for material, keywords in self.material_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        attributes['materials'].append(material)
                        break
            
            # Extract colors (basic color detection)
            colors = ['white', 'black', 'brown', 'gray', 'grey', 'blue', 'red', 'green', 
                     'yellow', 'orange', 'purple', 'pink', 'beige', 'cream', 'natural']
            for color in colors:
                if color in text_lower:
                    attributes['colors'].append(color)
            
            # Extract features (basic feature detection)
            features = ['adjustable', 'storage', 'comfortable', 'modern', 'vintage', 
                       'ergonomic', 'durable', 'lightweight', 'foldable', 'waterproof']
            for feature in features:
                if feature in text_lower:
                    attributes['features'].append(feature)
            
            # Remove duplicates
            for key in attributes:
                attributes[key] = list(set(attributes[key]))
            
            return attributes
            
        except Exception as e:
            print(f\"Error extracting attributes: {str(e)}\")
            return {'furniture_types': [], 'rooms': [], 'styles': [], 'materials': [], 'colors': [], 'features': []}
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        \"\"\"
        Calculate semantic similarity between two texts
        \"\"\"
        try:
            if self.sentence_model:
                # Use sentence embeddings for better similarity
                embeddings = self.sentence_model.encode([text1, text2])
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                return float(similarity)
            else:
                # Fallback to simple word overlap
                words1 = set(text1.lower().split())
                words2 = set(text2.lower().split())
                intersection = words1.intersection(words2)
                union = words1.union(words2)
                return len(intersection) / len(union) if union else 0.0
                
        except Exception as e:
            print(f\"Error calculating similarity: {str(e)}\")
            return 0.0
    
    def analyze_search_intent(self, query: str) -> Dict[str, Any]:
        \"\"\"
        Analyze user search intent and provide structured information
        \"\"\"
        try:
            intent_analysis = {
                'original_query': query,
                'processed_query': self.process_query(query),
                'furniture_intent': self._extract_furniture_intent(query.lower()),
                'room_context': self._extract_room_context(query.lower()),
                'style_context': self._extract_style_context(query.lower()),
                'material_context': self._extract_material_context(query.lower()),
                'query_type': self._determine_query_type(query),
                'confidence': self._calculate_intent_confidence(query)
            }
            
            return intent_analysis
            
        except Exception as e:
            print(f\"Error analyzing search intent: {str(e)}\")
            return {'original_query': query, 'processed_query': query, 'query_type': 'general'}
    
    def _determine_query_type(self, query: str) -> str:
        \"\"\"Determine the type of user query\"\"\"
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['recommend', 'suggest', 'find me', 'looking for']):
            return 'recommendation'
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            return 'comparison'
        elif any(word in query_lower for word in ['cheap', 'affordable', 'budget', 'under']):
            return 'price_sensitive'
        elif any(word in query_lower for word in ['luxury', 'premium', 'high-end', 'expensive']):
            return 'premium'
        elif any(word in query_lower for word in ['similar', 'like', 'same as']):
            return 'similarity'
        else:
            return 'general'
    
    def _calculate_intent_confidence(self, query: str) -> float:
        \"\"\"Calculate confidence score for intent recognition\"\"\"
        try:
            total_keywords = 0
            matched_keywords = 0
            
            query_lower = query.lower()
            
            # Check all keyword categories
            all_keywords = []
            all_keywords.extend([kw for kwlist in self.furniture_keywords.values() for kw in kwlist])
            all_keywords.extend([kw for kwlist in self.room_categories.values() for kw in kwlist])
            all_keywords.extend([kw for kwlist in self.style_keywords.values() for kw in kwlist])
            all_keywords.extend([kw for kwlist in self.material_keywords.values() for kw in kwlist])
            
            # Count matches
            for keyword in all_keywords:
                total_keywords += 1
                if keyword in query_lower:
                    matched_keywords += 1
            
            # Calculate confidence based on keyword matches
            if total_keywords > 0:
                base_confidence = matched_keywords / total_keywords
                # Boost confidence for longer, more specific queries
                length_factor = min(len(query.split()) / 10, 1.0)
                final_confidence = min(base_confidence + length_factor * 0.3, 1.0)
                return final_confidence
            else:
                return 0.5  # Default confidence
                
        except Exception as e:
            print(f\"Error calculating confidence: {str(e)}\")
            return 0.5"