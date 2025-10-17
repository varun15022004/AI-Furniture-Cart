import os
import logging
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime

# Try to import OpenAI, but make it optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIDescriptionGenerator:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the AI description generator
        
        Args:
            api_key: OpenAI API key (optional, can be set via environment variable)
            model: OpenAI model to use for generation
        """
        self.model = model
        self.client = None
        
        if OPENAI_AVAILABLE:
            # Get API key from parameter or environment
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            
            if self.api_key:
                try:
                    openai.api_key = self.api_key
                    self.client = openai.OpenAI(api_key=self.api_key)
                    logger.info("OpenAI client initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI client: {e}")
                    self.client = None
            else:
                logger.warning("OpenAI API key not found. AI description generation will use fallback methods.")
        else:
            logger.warning("OpenAI not available. AI description generation will use fallback methods.")
    
    async def generate_description(self, product_data: Dict[str, Any]) -> str:
        """
        Generate an AI description for a product
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Generated product description
        """
        try:
            if self.client and self.api_key:
                return await self._generate_with_openai(product_data)
            else:
                return await self._generate_fallback_description(product_data)
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return await self._generate_fallback_description(product_data)
    
    async def _generate_with_openai(self, product_data: Dict[str, Any]) -> str:
        """Generate description using OpenAI API"""
        try:
            # Create a prompt based on available product data
            prompt = self._create_prompt(product_data)
            
            # Call OpenAI API
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional furniture product description writer. Create engaging, informative, and SEO-friendly product descriptions that highlight key features and benefits."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            logger.info("Generated description using OpenAI")
            return description
            
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            return await self._generate_fallback_description(product_data)
    
    def _create_prompt(self, product_data: Dict[str, Any]) -> str:
        """Create a prompt for AI description generation"""
        title = product_data.get('title', 'Unknown Product')
        category = product_data.get('categories_clean', '')
        material = product_data.get('material_norm', '')
        brand = product_data.get('brand_norm', '')
        price = product_data.get('price_num', 0)
        color = product_data.get('color_norm', '')
        
        # Extract categories if they're in JSON format
        if category:
            try:
                if isinstance(category, str):
                    categories = json.loads(category.replace("'", '"'))
                    if isinstance(categories, list):
                        category = ', '.join(categories)
                    else:
                        category = str(categories)
            except:
                pass
        
        prompt_parts = [
            f"Write a compelling product description for: {title}",
        ]
        
        if category:
            prompt_parts.append(f"Category: {category}")
        if material:
            prompt_parts.append(f"Material: {material}")
        if brand:
            prompt_parts.append(f"Brand: {brand}")
        if color:
            prompt_parts.append(f"Color: {color}")
        if price and price > 0:
            prompt_parts.append(f"Price: ${price:.2f}")
        
        prompt_parts.extend([
            "",
            "The description should be:",
            "- 2-3 sentences long",
            "- Highlight key features and benefits",
            "- Use persuasive language",
            "- Be suitable for e-commerce",
            "- Focus on quality and craftsmanship"
        ])
        
        return "\n".join(prompt_parts)
    
    async def _generate_fallback_description(self, product_data: Dict[str, Any]) -> str:
        """Generate a basic description using template-based approach"""
        try:
            title = product_data.get('title', 'Product')
            category = product_data.get('categories_clean', '')
            material = product_data.get('material_norm', '')
            brand = product_data.get('brand_norm', '')
            price = product_data.get('price_num', 0)
            
            # Extract first category if multiple
            if category:
                try:
                    if isinstance(category, str):
                        categories = json.loads(category.replace("'", '"'))
                        if isinstance(categories, list) and categories:
                            category = categories[0]
                        else:
                            category = str(categories)
                except:
                    pass
            
            # Template-based generation
            description_parts = []
            
            # Opening line
            if category and 'chair' in category.lower():
                description_parts.append(f"Experience superior comfort and style with this {title.lower()}.")
            elif category and 'table' in category.lower():
                description_parts.append(f"Enhance your space with this elegant {title.lower()}.")
            elif category and 'bed' in category.lower():
                description_parts.append(f"Transform your bedroom with this luxurious {title.lower()}.")
            else:
                description_parts.append(f"Discover the perfect addition to your home with this {title.lower()}.")
            
            # Material and craftsmanship
            if material:
                if 'wood' in material.lower():
                    description_parts.append(f"Crafted from premium {material.lower()}, this piece combines durability with timeless appeal.")
                elif 'metal' in material.lower():
                    description_parts.append(f"Built with sturdy {material.lower()} construction for lasting quality and modern aesthetics.")
                elif 'fabric' in material.lower() or 'upholstered' in material.lower():
                    description_parts.append(f"Features high-quality {material.lower()} upholstery for ultimate comfort and sophistication.")
                else:
                    description_parts.append(f"Made with quality {material.lower()} materials for exceptional durability.")
            else:
                description_parts.append("Built with attention to detail and quality craftsmanship.")
            
            # Brand and value proposition
            if brand and brand.lower() != 'unknown':
                description_parts.append(f"From {brand}, this piece represents excellent value and reliable quality for your home.")
            else:
                description_parts.append("Perfect for modern homes seeking style and functionality.")
            
            description = " ".join(description_parts)
            
            logger.info("Generated fallback description")
            return description
            
        except Exception as e:
            logger.error(f"Error in fallback description generation: {e}")
            return f"Quality furniture piece perfect for any home. {product_data.get('title', 'Product')} offers style and functionality."
    
    async def generate_bulk_descriptions(self, products_data: list) -> Dict[str, str]:
        """
        Generate descriptions for multiple products
        
        Args:
            products_data: List of product dictionaries
            
        Returns:
            Dictionary mapping product IDs to descriptions
        """
        descriptions = {}
        
        # Limit concurrent requests to avoid API rate limits
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def generate_single(product):
            async with semaphore:
                try:
                    product_id = product.get('uniq_id', str(hash(str(product))))
                    description = await self.generate_description(product)
                    descriptions[product_id] = description
                    await asyncio.sleep(0.1)  # Small delay to avoid rate limiting
                except Exception as e:
                    logger.error(f"Error generating description for product {product.get('uniq_id', 'unknown')}: {e}")
        
        # Create tasks for all products
        tasks = [generate_single(product) for product in products_data]
        
        # Execute all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"Generated descriptions for {len(descriptions)} products")
        return descriptions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generator statistics"""
        return {
            "openai_available": OPENAI_AVAILABLE,
            "client_initialized": self.client is not None,
            "model": self.model,
            "api_key_configured": bool(getattr(self, 'api_key', None))
        }
    
    async def generate_category_descriptions(self, categories: list) -> Dict[str, str]:
        """Generate descriptions for product categories"""
        descriptions = {}
        
        for category in categories:
            try:
                if self.client and self.api_key:
                    prompt = f"""
                    Write a 2-3 sentence marketing description for the furniture category: {category}
                    
                    The description should:
                    - Highlight what makes this category special
                    - Appeal to potential customers
                    - Be engaging and informative
                    - Focus on lifestyle benefits
                    """
                    
                    response = await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a furniture marketing expert."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    
                    descriptions[category] = response.choices[0].message.content.strip()
                else:
                    # Fallback category descriptions
                    if 'living' in category.lower():
                        descriptions[category] = "Create your perfect living space with our comfortable and stylish furniture collection. From elegant sofas to functional coffee tables, find pieces that bring family and friends together."
                    elif 'bedroom' in category.lower():
                        descriptions[category] = "Transform your bedroom into a peaceful retreat with our carefully curated furniture selection. Discover beds, dressers, and nightstands that combine comfort with sophisticated design."
                    elif 'office' in category.lower():
                        descriptions[category] = "Enhance your productivity with our professional office furniture collection. Ergonomic chairs, functional desks, and storage solutions designed for the modern workplace."
                    else:
                        descriptions[category] = f"Explore our {category.lower()} collection featuring quality furniture pieces designed to enhance your home with style and functionality."
                        
                await asyncio.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error generating category description for {category}: {e}")
                descriptions[category] = f"Quality {category.lower()} furniture for your home."
        
        return descriptions