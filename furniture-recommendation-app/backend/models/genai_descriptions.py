import os
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser
from typing import List, Dict, Any, Optional
import json
import random

class GenAIDescriptionGenerator:
    """
    Generative AI description generator using LangChain
    Creates creative and engaging product descriptions for furniture recommendations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.llm = None
        self.description_chain = None
        self.conversation_chain = None
        
        # Fallback templates for when API is not available
        self.fallback_templates = self._load_fallback_templates()
        
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Initialize LangChain components"""
        try:
            if self.api_key:
                # Initialize OpenAI LLM
                os.environ["OPENAI_API_KEY"] = self.api_key
                self.llm = OpenAI(
                    temperature=0.7,
                    max_tokens=300,
                    model_name="gpt-3.5-turbo-instruct"
                )
                
                # Create prompt templates
                description_prompt = PromptTemplate(
                    input_variables=["products", "user_query", "context"],
                    template=self._get_description_template()
                )
                
                conversation_prompt = PromptTemplate(
                    input_variables=["products", "user_message", "conversation_context"],
                    template=self._get_conversation_template()
                )
                
                # Create LangChain chains
                self.description_chain = LLMChain(
                    llm=self.llm,
                    prompt=description_prompt,
                    verbose=False
                )
                
                self.conversation_chain = LLMChain(
                    llm=self.llm,
                    prompt=conversation_prompt,
                    verbose=False
                )
                
                print("GenAI Description Generator initialized successfully with OpenAI")
                
            else:
                print("Warning: OpenAI API key not found. Using fallback description generation.")
                
        except Exception as e:
            print(f"Error initializing LangChain: {str(e)}. Using fallback description generation.")
            self.llm = None
    
    def _get_description_template(self) -> str:
        """Get the prompt template for product descriptions"""
        return \"\"\"You are a creative furniture consultant and copywriter. Create an engaging, personalized description for furniture recommendations.

User Query: {user_query}
Context: {context}

Recommended Products:
{products}

Please write a warm, conversational response that:
1. Acknowledges the user's specific needs mentioned in their query
2. Briefly highlights why these particular pieces were chosen for them
3. Describes 2-3 key features or benefits of the recommended items
4. Uses descriptive, appealing language that helps them visualize the furniture in their space
5. Maintains an enthusiastic but not overly sales-y tone
6. Keeps the response concise (2-3 paragraphs maximum)

Response:\"\"\"
    
    def _get_conversation_template(self) -> str:
        """Get the prompt template for conversational responses"""
        return \"\"\"You are a helpful furniture shopping assistant having a friendly conversation with a customer.

Customer Message: {user_message}
Conversation Context: {conversation_context}

Recommended Products:
{products}

Create a natural, conversational response that:
1. Directly addresses what the customer said
2. Provides helpful information about the recommended furniture
3. Asks a follow-up question to keep the conversation going
4. Maintains a friendly, knowledgeable tone
5. Offers practical advice when relevant

Response:\"\"\"
    
    def _load_fallback_templates(self) -> Dict[str, List[str]]:
        """Load fallback templates for when GenAI is not available"""
        return {
            'general': [
                \"Based on your preferences, I've found some excellent {category} options that would work perfectly in your {room}. {product_highlight} These pieces combine {style} design with {material} construction, offering both style and durability.\",
                \"Here are some fantastic {category} recommendations that caught my attention! {product_highlight} The {style} aesthetic and {material} materials make these pieces both functional and beautiful.\",
                \"I think you'll love these {category} selections - they're perfect for what you're looking for! {product_highlight} Each piece features quality {material} construction with that {style} look you mentioned.\"
            ],
            'budget': [
                \"Great news! I found some excellent {category} options within your budget. {product_highlight} These pieces offer amazing value with {material} construction and {style} design.\",
                \"Here are some budget-friendly {category} recommendations that don't compromise on quality! {product_highlight} You're getting great {style} style with durable {material} materials.\"
            ],
            'luxury': [
                \"For your luxury {category} search, I've selected some exceptional pieces. {product_highlight} These premium items feature exquisite {material} craftsmanship with sophisticated {style} design.\",
                \"Here are some high-end {category} recommendations that exemplify luxury and quality. {product_highlight} Each piece showcases superior {material} construction with elegant {style} aesthetics.\"
            ],
            'specific_room': [
                \"Perfect {category} selections for your {room}! {product_highlight} These pieces are specifically chosen to complement a {room} setting with {style} design and {material} construction.\",
                \"I've found some ideal {category} options that would work beautifully in your {room}. {product_highlight} The {style} style and {material} materials make them perfect for this space.\"
            ]
        }
    
    def generate_description(self, products: List[Dict[str, Any]], user_query: str, 
                           context: Optional[str] = None) -> str:
        \"\"\"
        Generate creative product description using GenAI or fallback methods
        \"\"\"
        try:
            if self.llm and self.description_chain:
                return self._generate_with_llm(products, user_query, context or \"\")
            else:
                return self._generate_fallback_description(products, user_query, context)
                
        except Exception as e:
            print(f\"Error generating description: {str(e)}\")
            return self._generate_fallback_description(products, user_query, context)
    
    def _generate_with_llm(self, products: List[Dict[str, Any]], user_query: str, 
                          context: str) -> str:
        \"\"\"Generate description using LangChain and OpenAI\"\"\"
        try:
            # Format products for the prompt
            products_text = self._format_products_for_prompt(products)
            
            # Generate description using LangChain
            response = self.description_chain.run(
                products=products_text,
                user_query=user_query,
                context=context
            )
            
            return response.strip()
            
        except Exception as e:
            print(f\"Error in LLM generation: {str(e)}\")
            return self._generate_fallback_description(products, user_query, context)
    
    def _generate_fallback_description(self, products: List[Dict[str, Any]], 
                                     user_query: str, context: Optional[str]) -> str:
        \"\"\"Generate description using fallback templates\"\"\"
        try:
            if not products:
                return \"I apologize, but I couldn't find any suitable products for your request. Please try adjusting your search criteria.\"
            
            # Extract key information from products and query
            product_info = self._extract_product_info(products)
            query_info = self._analyze_query_intent(user_query)
            
            # Select appropriate template category
            template_category = self._select_template_category(query_info)
            
            # Get random template from selected category
            templates = self.fallback_templates.get(template_category, self.fallback_templates['general'])
            template = random.choice(templates)
            
            # Create product highlights
            product_highlight = self._create_product_highlights(products[:3])  # Focus on top 3
            
            # Format the template
            description = template.format(
                category=product_info.get('primary_category', 'furniture'),
                room=query_info.get('room', 'space'),
                product_highlight=product_highlight,
                style=product_info.get('style', 'modern'),
                material=product_info.get('material', 'quality')
            )
            
            # Add specific product mentions
            if len(products) > 0:
                description += f\" I especially recommend the {products[0].get('title', 'first item')}\"
                if len(products) > 1:
                    description += f\" and the {products[1].get('title', 'second item')}\""
                description += \" for your needs.\"
            
            return description
            
        except Exception as e:
            print(f\"Error in fallback generation: {str(e)}\")
            return \"Here are some great furniture recommendations that match your preferences!\"
    
    def _format_products_for_prompt(self, products: List[Dict[str, Any]]) -> str:
        \"\"\"Format products for inclusion in prompts\"\"\"
        formatted_products = []
        
        for i, product in enumerate(products[:5], 1):  # Limit to top 5
            product_text = f\"{i}. {product.get('title', 'Unknown Product')}\"
            
            if product.get('brand'):
                product_text += f\" by {product['brand']}\"
            
            if product.get('price'):
                product_text += f\" - ${product['price']}\"
            
            if product.get('description'):
                # Truncate long descriptions
                desc = str(product['description'])[:100]
                if len(str(product['description'])) > 100:
                    desc += \"...\"\n                product_text += f\" - {desc}\"\n            \n            if product.get('categories'):\n                product_text += f\" (Category: {product['categories']})\"\n            \n            formatted_products.append(product_text)\n        \n        return \"\\n\".join(formatted_products)\n    \n    def _extract_product_info(self, products: List[Dict[str, Any]]) -> Dict[str, str]:\n        \"\"\"Extract common information from products\"\"\"\n        info = {\n            'primary_category': 'furniture',\n            'style': 'modern',\n            'material': 'quality'\n        }\n        \n        if products:\n            # Extract primary category from first product\n            first_product = products[0]\n            categories = first_product.get('categories', '')\n            if categories:\n                # Extract last part of category (most specific)\n                category_parts = categories.split(' > ')\n                if category_parts:\n                    info['primary_category'] = category_parts[-1].lower()\n            \n            # Extract style keywords\n            combined_text = ' '.join([\n                str(p.get('title', '')) + ' ' + \n                str(p.get('description', '')) + ' ' +\n                str(p.get('categories', ''))\n                for p in products[:3]\n            ]).lower()\n            \n            style_keywords = {\n                'modern': ['modern', 'contemporary', 'sleek', 'minimalist'],\n                'traditional': ['traditional', 'classic', 'elegant', 'formal'],\n                'rustic': ['rustic', 'farmhouse', 'country', 'vintage'],\n                'industrial': ['industrial', 'urban', 'metal', 'concrete']\n            }\n            \n            for style, keywords in style_keywords.items():\n                if any(keyword in combined_text for keyword in keywords):\n                    info['style'] = style\n                    break\n            \n            # Extract material information\n            material_keywords = {\n                'wood': ['wood', 'oak', 'pine', 'teak'],\n                'metal': ['metal', 'steel', 'iron', 'aluminum'],\n                'fabric': ['fabric', 'velvet', 'leather', 'cotton'],\n                'glass': ['glass', 'crystal']\n            }\n            \n            for material, keywords in material_keywords.items():\n                if any(keyword in combined_text for keyword in keywords):\n                    info['material'] = material\n                    break\n        \n        return info\n    \n    def _analyze_query_intent(self, query: str) -> Dict[str, str]:\n        \"\"\"Analyze user query for intent and context\"\"\"\n        query_lower = query.lower()\n        intent_info = {'room': 'home'}\n        \n        # Room detection\n        room_keywords = {\n            'living room': ['living room', 'lounge', 'family room'],\n            'bedroom': ['bedroom', 'bed room', 'sleep'],\n            'dining room': ['dining room', 'dining area', 'eat'],\n            'office': ['office', 'study', 'work'],\n            'kitchen': ['kitchen', 'cook']\n        }\n        \n        for room, keywords in room_keywords.items():\n            if any(keyword in query_lower for keyword in keywords):\n                intent_info['room'] = room\n                break\n        \n        return intent_info\n    \n    def _select_template_category(self, query_info: Dict[str, str]) -> str:\n        \"\"\"Select appropriate template category based on query analysis\"\"\"\n        # This could be expanded with more sophisticated intent classification\n        return 'general'\n    \n    def _create_product_highlights(self, products: List[Dict[str, Any]]) -> str:\n        \"\"\"Create highlights for the top products\"\"\"\n        if not products:\n            return \"These items offer great value and style.\"\n        \n        highlights = []\n        for product in products:\n            title = product.get('title', 'This piece')\n            price = product.get('price')\n            \n            highlight = f\"{title}\"\n            if price:\n                highlight += f\" (${price})\"\n            \n            # Add a brief feature if available\n            description = product.get('description', '')\n            if description and len(description) > 20:\n                # Extract first meaningful phrase\n                desc_words = description.split()[:8]\n                highlight += f\" - {' '.join(desc_words)}\"\n                if len(description.split()) > 8:\n                    highlight += \"...\"\n            \n            highlights.append(highlight)\n        \n        if len(highlights) == 1:\n            return highlights[0] + \" stands out for its exceptional design.\"\n        elif len(highlights) == 2:\n            return f\"{highlights[0]} and {highlights[1]} both offer excellent value.\"\n        else:\n            return f\"{highlights[0]}, {highlights[1]}, and {highlights[2]} each bring unique appeal to your space.\"\n    \n    def generate_conversation_response(self, products: List[Dict[str, Any]], \n                                     user_message: str, \n                                     conversation_context: Optional[str] = None) -> str:\n        \"\"\"Generate conversational response for chat interface\"\"\"\n        try:\n            if self.llm and self.conversation_chain:\n                return self._generate_conversation_with_llm(products, user_message, conversation_context or \"\")\n            else:\n                return self._generate_conversation_fallback(products, user_message, conversation_context)\n                \n        except Exception as e:\n            print(f\"Error generating conversation response: {str(e)}\")\n            return self._generate_conversation_fallback(products, user_message, conversation_context)\n    \n    def _generate_conversation_with_llm(self, products: List[Dict[str, Any]], \n                                      user_message: str, conversation_context: str) -> str:\n        \"\"\"Generate conversational response using LLM\"\"\"\n        try:\n            products_text = self._format_products_for_prompt(products)\n            \n            response = self.conversation_chain.run(\n                products=products_text,\n                user_message=user_message,\n                conversation_context=conversation_context\n            )\n            \n            return response.strip()\n            \n        except Exception as e:\n            print(f\"Error in LLM conversation generation: {str(e)}\")\n            return self._generate_conversation_fallback(products, user_message, conversation_context)\n    \n    def _generate_conversation_fallback(self, products: List[Dict[str, Any]], \n                                      user_message: str, \n                                      conversation_context: Optional[str]) -> str:\n        \"\"\"Generate conversational response using templates\"\"\"\n        try:\n            if not products:\n                return \"I'm sorry, I couldn't find any products matching your criteria. Could you tell me more about what you're looking for?\"\n            \n            # Simple conversational responses\n            conversation_templates = [\n                f\"Great choice! I found {len(products)} items that match what you're looking for. {self._create_product_highlights(products[:2])} Would you like to know more about any specific piece?\",\n                f\"Perfect! Here are {len(products)} recommendations based on your preferences. {self._create_product_highlights(products[:2])} Which style appeals to you most?\",\n                f\"Excellent! I've got {len(products)} great options for you. {self._create_product_highlights(products[:2])} Are you interested in learning more about the materials or dimensions?\"\n            ]\n            \n            return random.choice(conversation_templates)\n            \n        except Exception as e:\n            print(f\"Error in conversation fallback: {str(e)}\")\n            return \"I've found some great furniture options for you! Let me know if you'd like more details about any of them.\"\n    \n    def enhance_product_descriptions(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:\n        \"\"\"Enhance individual product descriptions\"\"\"\n        enhanced_products = []\n        \n        for product in products:\n            enhanced_product = product.copy()\n            \n            try:\n                # Generate enhanced description for each product\n                original_desc = product.get('description', '')\n                title = product.get('title', 'Product')\n                \n                if self.llm:\n                    # Use LLM for enhancement\n                    enhancement_prompt = f\"Enhance this furniture product description to be more appealing and detailed: {title} - {original_desc}\"\n                    enhanced_desc = self.llm(enhancement_prompt, max_tokens=150)\n                    enhanced_product['enhanced_description'] = enhanced_desc.strip()\n                else:\n                    # Use template-based enhancement\n                    enhanced_product['enhanced_description'] = self._enhance_description_fallback(product)\n                \n                enhanced_products.append(enhanced_product)\n                \n            except Exception as e:\n                print(f\"Error enhancing product description: {str(e)}\")\n                enhanced_products.append(product)\n        \n        return enhanced_products\n    \n    def _enhance_description_fallback(self, product: Dict[str, Any]) -> str:\n        \"\"\"Enhance product description using templates\"\"\"\n        try:\n            original_desc = product.get('description', '')\n            title = product.get('title', 'This piece')\n            \n            enhancement_templates = [\n                f\"{title} {original_desc} Perfect for creating a stylish and comfortable living space.\",\n                f\"Experience the quality of {title}. {original_desc} An excellent addition to any modern home.\",\n                f\"{title} combines functionality with aesthetic appeal. {original_desc} Transform your space with this versatile piece.\"\n            ]\n            \n            return random.choice(enhancement_templates)\n            \n        except Exception as e:\n            print(f\"Error in description enhancement fallback: {str(e)}\")\n            return product.get('description', 'A quality furniture piece for your home.')\n    \n    def get_generation_stats(self) -> Dict[str, Any]:\n        \"\"\"Get statistics about the generation service\"\"\"\n        return {\n            'llm_available': self.llm is not None,\n            'api_key_configured': self.api_key is not None,\n            'fallback_templates_count': sum(len(templates) for templates in self.fallback_templates.values()),\n            'supported_categories': list(self.fallback_templates.keys())\n        }