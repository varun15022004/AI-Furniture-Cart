import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
import uuid
from datetime import datetime
import os

class VectorDatabase:
    """
    Vector database integration using ChromaDB for storing and retrieving
    furniture product embeddings and user interactions
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.products_collection = None
        self.interactions_collection = None
        self.sentence_model = None
        
        self._initialize_database()
        self._initialize_sentence_model()
        
    def _initialize_database(self):
        """Initialize ChromaDB client and collections"""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Create or get collections
            self.products_collection = self.client.get_or_create_collection(
                name="furniture_products",
                metadata={"hnsw:space": "cosine"}
            )
            
            self.interactions_collection = self.client.get_or_create_collection(
                name="user_interactions",
                metadata={"hnsw:space": "cosine"}
            )
            
            print(f"Vector database initialized with {self.products_collection.count()} products")
            
        except Exception as e:
            print(f"Error initializing vector database: {str(e)}")
            # Fallback to in-memory database
            try:
                self.client = chromadb.Client()
                self.products_collection = self.client.get_or_create_collection("furniture_products")
                self.interactions_collection = self.client.get_or_create_collection("user_interactions")
                print("Using in-memory vector database as fallback")
            except Exception as e2:
                print(f"Failed to initialize fallback database: {str(e2)}")
                self.client = None
    
    def _initialize_sentence_model(self):
        """Initialize sentence transformer model for embeddings"""
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Sentence transformer model loaded for vector database")
        except Exception as e:
            print(f"Error loading sentence transformer: {str(e)}")
            self.sentence_model = None
    
    def store_products(self, products_df: pd.DataFrame) -> bool:
        """
        Store product data and embeddings in the vector database
        """
        if not self.client or not self.products_collection:
            print("Vector database not available")
            return False
        
        try:
            # Clear existing products
            # self.products_collection.delete(where={})
            
            embeddings = []
            documents = []
            metadatas = []
            ids = []
            
            for _, product in products_df.iterrows():
                # Create document text for embedding
                doc_text = self._create_product_document(product)
                documents.append(doc_text)
                
                # Generate embedding
                if self.sentence_model:
                    embedding = self.sentence_model.encode(doc_text).tolist()
                else:
                    # Fallback: create dummy embedding
                    embedding = [0.0] * 384  # MiniLM embedding dimension
                
                embeddings.append(embedding)
                
                # Prepare metadata
                metadata = {
                    'title': str(product.get('title', '')),
                    'brand': str(product.get('brand', '')),
                    'price': float(product.get('price', 0.0)) if pd.notna(product.get('price')) else 0.0,
                    'categories': str(product.get('categories', '')),
                    'material': str(product.get('material', '')),
                    'color': str(product.get('color', '')),
                    'description': str(product.get('description', ''))[:500]  # Limit length
                }
                metadatas.append(metadata)
                
                # Create unique ID
                product_id = str(product.get('uniq_id', f"product_{uuid.uuid4()}"))
                ids.append(product_id)
            
            # Add to collection in batches
            batch_size = 50
            for i in range(0, len(embeddings), batch_size):
                batch_end = min(i + batch_size, len(embeddings))
                
                self.products_collection.add(
                    embeddings=embeddings[i:batch_end],
                    documents=documents[i:batch_end],
                    metadatas=metadatas[i:batch_end],
                    ids=ids[i:batch_end]
                )
            
            print(f"Stored {len(embeddings)} products in vector database")
            return True
            
        except Exception as e:
            print(f"Error storing products in vector database: {str(e)}")
            return False
    
    def _create_product_document(self, product: pd.Series) -> str:
        """Create searchable document text from product data"""
        doc_parts = []
        
        # Add title (most important)
        title = product.get('title', '')
        if title:
            doc_parts.append(f"Title: {title}")
        
        # Add description
        description = product.get('description', '')
        if description:
            doc_parts.append(f"Description: {description}")
        
        # Add category
        categories = product.get('categories', '')
        if categories:
            doc_parts.append(f"Category: {categories}")
        
        # Add brand
        brand = product.get('brand', '')
        if brand:
            doc_parts.append(f"Brand: {brand}")
        
        # Add material
        material = product.get('material', '')
        if material:
            doc_parts.append(f"Material: {material}")
        
        # Add color
        color = product.get('color', '')
        if color:
            doc_parts.append(f"Color: {color}")
        
        # Add price range
        price = product.get('price', 0)
        if price and pd.notna(price):
            if price < 200:
                doc_parts.append("Price range: budget-friendly affordable")
            elif price < 500:
                doc_parts.append("Price range: mid-range moderate")
            elif price < 1000:
                doc_parts.append("Price range: premium quality")
            else:
                doc_parts.append("Price range: luxury high-end")
        
        return " ".join(doc_parts)
    
    def semantic_search(self, query: str, max_results: int = 10, 
                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search for products based on query
        """
        if not self.client or not self.products_collection:
            print("Vector database not available")
            return []
        
        try:
            # Generate query embedding
            if self.sentence_model:
                query_embedding = self.sentence_model.encode(query).tolist()
            else:
                print("Sentence model not available for semantic search")
                return []
            
            # Prepare where clause for filtering
            where_clause = {}
            if filters:
                # Convert filters to ChromaDB where format
                if 'min_price' in filters or 'max_price' in filters:
                    price_conditions = {}
                    if 'min_price' in filters:
                        price_conditions['$gte'] = filters['min_price']
                    if 'max_price' in filters:
                        price_conditions['$lte'] = filters['max_price']
                    where_clause['price'] = price_conditions
                
                # String filters
                for field in ['brand', 'categories', 'material', 'color']:
                    if field in filters and filters[field]:
                        where_clause[field] = {'$regex': f".*{filters[field]}.*"}
            
            # Perform vector search
            results = self.products_collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                where=where_clause if where_clause else None,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results and results['ids'] and len(results['ids']) > 0:
                for i, product_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    
                    # Convert distance to similarity score (cosine distance to similarity)
                    similarity_score = max(0.0, 1.0 - distance)
                    
                    product_data = {
                        'uniq_id': product_id,
                        'similarity_score': similarity_score,
                        **metadata
                    }
                    
                    formatted_results.append(product_data)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return []
    
    def store_interaction(self, user_query: str, recommendations: List[Dict[str, Any]], 
                         user_id: str = "anonymous") -> bool:
        """
        Store user interaction for learning and analytics
        """
        if not self.client or not self.interactions_collection:
            return False
        
        try:
            # Create interaction document
            interaction_doc = f"Query: {user_query} "
            if recommendations:
                rec_titles = [rec.get('title', '') for rec in recommendations[:3]]
                interaction_doc += f"Recommendations: {', '.join(rec_titles)}"
            
            # Generate embedding for the interaction
            if self.sentence_model:
                interaction_embedding = self.sentence_model.encode(interaction_doc).tolist()
            else:
                interaction_embedding = [0.0] * 384
            
            # Prepare interaction metadata
            interaction_metadata = {
                'user_id': user_id,
                'query': user_query[:500],  # Limit length
                'timestamp': datetime.now().isoformat(),
                'num_recommendations': len(recommendations),
                'recommendation_ids': [str(rec.get('uniq_id', '')) for rec in recommendations[:5]]
            }
            
            # Store interaction
            interaction_id = str(uuid.uuid4())
            self.interactions_collection.add(
                embeddings=[interaction_embedding],
                documents=[interaction_doc],
                metadatas=[interaction_metadata],
                ids=[interaction_id]
            )
            
            return True
            
        except Exception as e:
            print(f"Error storing interaction: {str(e)}")
            return False
    
    def get_similar_queries(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar past queries for better recommendations
        """
        if not self.client or not self.interactions_collection:
            return []
        
        try:
            # Generate query embedding
            if self.sentence_model:
                query_embedding = self.sentence_model.encode(query).tolist()
            else:
                return []
            
            # Search for similar interactions
            results = self.interactions_collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                include=['metadatas', 'distances']
            )
            
            # Format results
            similar_queries = []
            if results and results['ids'] and len(results['ids']) > 0:
                for i, interaction_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    
                    similarity_score = max(0.0, 1.0 - distance)
                    
                    similar_query = {
                        'interaction_id': interaction_id,
                        'similarity_score': similarity_score,
                        'original_query': metadata.get('query', ''),
                        'timestamp': metadata.get('timestamp', ''),
                        'recommendation_ids': metadata.get('recommendation_ids', [])
                    }
                    
                    similar_queries.append(similar_query)
            
            return similar_queries
            
        except Exception as e:
            print(f"Error finding similar queries: {str(e)}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific product by ID
        """
        if not self.client or not self.products_collection:
            return None
        
        try:
            results = self.products_collection.get(
                ids=[product_id],
                include=['metadatas']
            )
            
            if results and results['ids'] and len(results['ids']) > 0:
                metadata = results['metadatas'][0] if results['metadatas'] else {}
                product_data = {
                    'uniq_id': product_id,
                    **metadata
                }
                return product_data
            
            return None
            
        except Exception as e:
            print(f"Error retrieving product by ID: {str(e)}")
            return None
    
    def update_product(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update product metadata
        """
        if not self.client or not self.products_collection:
            return False
        
        try:
            # Get current product
            current_product = self.get_product_by_id(product_id)
            if not current_product:
                return False
            
            # Update metadata
            updated_metadata = {**current_product, **updates}
            
            # Update in collection
            self.products_collection.update(
                ids=[product_id],
                metadatas=[updated_metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating product: {str(e)}")
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from the database
        """
        if not self.client or not self.products_collection:
            return False
        
        try:
            self.products_collection.delete(ids=[product_id])
            return True
            
        except Exception as e:
            print(f"Error deleting product: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database
        """
        stats = {
            'database_available': self.client is not None,
            'products_count': 0,
            'interactions_count': 0,
            'sentence_model_available': self.sentence_model is not None
        }
        
        try:
            if self.products_collection:
                stats['products_count'] = self.products_collection.count()
            
            if self.interactions_collection:
                stats['interactions_count'] = self.interactions_collection.count()
                
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
        
        return stats
    
    def backup_data(self, backup_path: str) -> bool:
        """
        Backup vector database data
        """
        if not self.client:
            return False
        
        try:
            # Export products
            products_data = self.products_collection.get(include=['metadatas', 'documents'])
            
            # Export interactions
            interactions_data = self.interactions_collection.get(include=['metadatas', 'documents'])
            
            # Save to file
            backup_data = {
                'products': products_data,
                'interactions': interactions_data,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error backing up database: {str(e)}")
            return False
    
    def clear_all_data(self) -> bool:
        """
        Clear all data from the database (use with caution)
        """
        if not self.client:
            return False
        
        try:
            # Clear products
            if self.products_collection:
                self.products_collection.delete(where={})
            
            # Clear interactions
            if self.interactions_collection:
                self.interactions_collection.delete(where={})
            
            print("All data cleared from vector database")
            return True
            
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            return False