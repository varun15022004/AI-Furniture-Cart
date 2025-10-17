"""
Intelligent Chatbot Engine for Furniture E-commerce
Features:
- Natural language understanding for furniture queries
- Product recommendation based on conversation
- Context-aware responses
- Integration with AI engine for semantic search
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class FurnitureChatbot:
    """Intelligent chatbot for furniture product recommendations"""
    
    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        self.conversation_context = {}
        
        # Intent patterns for furniture queries
        self.intent_patterns = {
            'greeting': [
                r'hi|hello|hey|good morning|good afternoon|good evening',
                r'help|assist|support'
            ],
            'search_product': [
                r'looking for|need|want|searching for|find',
                r'show me|recommend|suggest',
                r'chair|sofa|table|bed|desk|cabinet|shelf|lamp|ottoman|bench'
            ],
            'price_query': [
                r'price|cost|budget|cheap|expensive|affordable',
                r'under \$?\d+|below \$?\d+|less than \$?\d+'
            ],
            'style_query': [
                r'modern|contemporary|rustic|vintage|industrial|scandinavian',
                r'style|design|look|aesthetic'
            ],
            'room_query': [
                r'living room|bedroom|kitchen|office|bathroom|dining room',
                r'for my|in my|room|space'
            ],
            'material_query': [
                r'wood|metal|leather|fabric|plastic|glass',
                r'material|made of|constructed'
            ],
            'size_query': [
                r'small|medium|large|big|compact|spacious',
                r'size|dimensions|fit'
            ],
            'goodbye': [
                r'bye|goodbye|thank you|thanks|that\'s all'
            ]
        }
        
        # Response templates
        self.response_templates = {
            'greeting': [
                "Hello! I'm your furniture assistant. How can I help you find the perfect piece for your home today?",
                "Hi there! Looking for some beautiful furniture? I'd love to help you find exactly what you need!",
                "Welcome! I'm here to help you discover amazing furniture pieces. What are you shopping for?"
            ],
            'clarification': [
                "Could you tell me more about what you're looking for?",
                "What specific type of furniture interests you?",
                "Are you looking for something for a particular room?"
            ],
            'no_results': [
                "I couldn't find exactly what you're looking for, but here are some similar options:",
                "Let me suggest some alternatives that might interest you:",
                "I found some related items that you might like:"
            ],
            'product_suggestion': [
                "Based on what you're looking for, I found these perfect matches:",
                "Here are some great options that fit your criteria:",
                "I think you'll love these pieces:"
            ],
            'goodbye': [
                "Thanks for chatting! Feel free to ask if you need more help finding furniture.",
                "Happy shopping! Let me know if you need any other recommendations.",
                "Goodbye! I hope you find the perfect furniture for your home."
            ]
        }
        
        # Product categories and synonyms
        self.category_synonyms = {
            'chair': ['chair', 'seat', 'seating', 'stool', 'armchair', 'recliner'],
            'sofa': ['sofa', 'couch', 'loveseat', 'sectional', 'settee'],
            'table': ['table', 'desk', 'surface', 'workstation'],
            'bed': ['bed', 'mattress', 'bedroom', 'sleeping'],
            'storage': ['storage', 'cabinet', 'shelf', 'bookcase', 'dresser', 'wardrobe'],
            'lighting': ['lamp', 'light', 'lighting', 'fixture']
        }
        
        # Room context
        self.room_furniture = {
            'living room': ['sofa', 'coffee table', 'tv stand', 'bookshelf', 'lamp', 'ottoman'],
            'bedroom': ['bed', 'nightstand', 'dresser', 'wardrobe', 'mirror'],
            'office': ['desk', 'office chair', 'bookshelf', 'filing cabinet'],
            'dining room': ['dining table', 'dining chair', 'buffet', 'china cabinet'],
            'kitchen': ['bar stool', 'kitchen island', 'storage cabinet']
        }
        
    def process_message(self, message: str, user_id: str = 'anonymous', 
                       conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process user message and return chatbot response with product suggestions"""
        
        try:
            # Initialize conversation context for user
            if user_id not in self.conversation_context:
                self.conversation_context[user_id] = {
                    'preferences': {},
                    'last_query': '',
                    'conversation_stage': 'greeting'
                }
            
            context = self.conversation_context[user_id]
            message_lower = message.lower().strip()
            
            # Extract intent and entities from message
            intent = self._extract_intent(message_lower)
            entities = self._extract_entities(message_lower)
            
            # Update context with extracted information
            context['preferences'].update(entities)
            context['last_query'] = message
            
            # Generate response based on intent
            response = self._generate_response(intent, entities, context, user_id)
            
            # Get product recommendations if applicable
            products = []
            if intent in ['search_product', 'price_query', 'style_query', 'room_query', 'material_query']:
                products = self._get_product_recommendations(entities, context, user_id)
            
            return {
                'response': response,
                'products': products,
                'intent': intent,
                'entities': entities,
                'conversation_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'has_suggestions': len(products) > 0
            }
            
        except Exception as e:
            logger.error(f"Error processing chatbot message: {e}")
            return {
                'response': "I'm sorry, I'm having trouble understanding right now. Could you try rephrasing that?",
                'products': [],
                'error': str(e)
            }
    
    def _extract_intent(self, message: str) -> str:
        """Extract user intent from message"""
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent
        
        # Default intent based on message content
        if any(word in message for word in ['chair', 'sofa', 'table', 'bed', 'furniture']):
            return 'search_product'
        
        return 'clarification'
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities like product type, price, style, etc."""
        
        entities = {}
        
        # Extract product category
        for category, synonyms in self.category_synonyms.items():
            if any(syn in message for syn in synonyms):
                entities['category'] = category
                break
        
        # Extract price range
        price_match = re.search(r'\$?(\d+)', message)
        if price_match:
            price = int(price_match.group(1))
            entities['max_price'] = price
            
        # Extract price keywords
        if 'cheap' in message or 'affordable' in message or 'budget' in message:
            entities['price_range'] = 'low'
        elif 'expensive' in message or 'premium' in message or 'luxury' in message:
            entities['price_range'] = 'high'
            
        # Extract style
        styles = ['modern', 'contemporary', 'rustic', 'vintage', 'industrial', 'scandinavian']
        for style in styles:
            if style in message:
                entities['style'] = style
                break
                
        # Extract room
        for room in self.room_furniture.keys():
            if room in message:
                entities['room'] = room
                break
                
        # Extract materials
        materials = ['wood', 'metal', 'leather', 'fabric', 'glass', 'plastic']
        for material in materials:
            if material in message:
                entities['material'] = material
                break
                
        # Extract size preferences
        if any(word in message for word in ['small', 'compact', 'mini']):
            entities['size_preference'] = 'small'
        elif any(word in message for word in ['large', 'big', 'spacious']):
            entities['size_preference'] = 'large'
            
        return entities
    
    def _generate_response(self, intent: str, entities: Dict, 
                          context: Dict, user_id: str) -> str:
        """Generate appropriate response based on intent and context"""
        
        if intent == 'greeting':
            return random.choice(self.response_templates['greeting'])
            
        elif intent == 'goodbye':
            return random.choice(self.response_templates['goodbye'])
            
        elif intent == 'search_product':
            if entities.get('category'):
                category = entities['category']
                response = f"Great! I can help you find the perfect {category}. "
                
                # Add contextual information
                if entities.get('room'):
                    response += f"For your {entities['room']}, "
                if entities.get('style'):
                    response += f"I'll look for {entities['style']} styles. "
                if entities.get('price_range'):
                    response += f"I'll focus on {entities['price_range']}-end options. "
                    
                response += "Let me show you some options:"
                return response
            else:
                return random.choice(self.response_templates['clarification'])
                
        elif intent in ['price_query', 'style_query', 'room_query', 'material_query']:
            return random.choice(self.response_templates['product_suggestion'])
            
        else:
            return random.choice(self.response_templates['clarification'])
    
    def _get_product_recommendations(self, entities: Dict, context: Dict, 
                                   user_id: str, limit: int = 6) -> List[Dict]:
        """Get product recommendations based on extracted entities"""
        
        try:
            # Build search query from entities
            query_parts = []
            
            if entities.get('category'):
                query_parts.append(entities['category'])
                
            if entities.get('style'):
                query_parts.append(entities['style'])
                
            if entities.get('room'):
                query_parts.append(entities['room'])
                
            if entities.get('material'):
                query_parts.append(entities['material'])
                
            search_query = ' '.join(query_parts) if query_parts else 'furniture'
            
            # Use AI engine for semantic search if available
            if self.ai_engine:
                # Build filters
                filters = {}
                if entities.get('max_price'):
                    filters['price'] = {'max': entities['max_price']}
                    
                results = self.ai_engine.semantic_search(search_query, limit, filters)
                
                # Format results for chatbot
                products = []
                for result in results:
                    products.append({
                        'id': result.get('product_id', ''),
                        'title': result.get('title', ''),
                        'price': result.get('price', 0),
                        'category': result.get('category', ''),
                        'description': result.get('ai_description', ''),
                        'similarity_score': result.get('similarity_score', 0),
                        'reason': self._generate_recommendation_reason(entities, result)
                    })
                
                return products
            else:
                # Fallback to simple recommendations
                return self._get_fallback_recommendations(entities, limit)
                
        except Exception as e:
            logger.error(f"Error getting product recommendations: {e}")
            return []
    
    def _generate_recommendation_reason(self, entities: Dict, product: Dict) -> str:
        """Generate a reason why this product was recommended"""
        
        reasons = []
        
        if entities.get('category') and entities['category'] in product.get('category', '').lower():
            reasons.append(f"matches your {entities['category']} request")
            
        if entities.get('style') and entities['style'] in product.get('description', '').lower():
            reasons.append(f"features {entities['style']} design")
            
        if entities.get('room'):
            reasons.append(f"perfect for your {entities['room']}")
            
        if not reasons:
            reasons.append("highly rated and popular choice")
            
        return reasons[0] if reasons else "recommended for you"
    
    def _get_fallback_recommendations(self, entities: Dict, limit: int) -> List[Dict]:
        """Fallback recommendations when AI engine is not available"""
        
        # This would typically query the database directly
        # For now, return mock recommendations
        mock_products = [
            {
                'id': 'mock-1',
                'title': 'Modern Office Chair',
                'price': 299.99,
                'category': 'chair',
                'description': 'Comfortable ergonomic chair for your workspace',
                'reason': 'popular choice for office furniture'
            },
            {
                'id': 'mock-2', 
                'title': 'Scandinavian Dining Table',
                'price': 599.99,
                'category': 'table',
                'description': 'Beautiful wooden table with clean lines',
                'reason': 'perfect for modern dining rooms'
            }
        ]
        
        # Filter based on entities if possible
        if entities.get('category'):
            mock_products = [p for p in mock_products if entities['category'] in p['category']]
            
        return mock_products[:limit]
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's conversation and preferences"""
        
        if user_id not in self.conversation_context:
            return {'preferences': {}, 'messages': 0}
            
        context = self.conversation_context[user_id]
        return {
            'preferences': context['preferences'],
            'last_query': context.get('last_query', ''),
            'conversation_stage': context.get('conversation_stage', 'greeting')
        }
    
    def reset_conversation(self, user_id: str):
        """Reset conversation context for a user"""
        if user_id in self.conversation_context:
            del self.conversation_context[user_id]