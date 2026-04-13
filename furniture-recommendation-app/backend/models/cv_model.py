import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import io
import numpy as np
from typing import Dict, Any, List, Tuple
import json
import os

class ComputerVisionModel:
    """
    Computer Vision model for furniture classification using ResNet18
    Classifies furniture types and categories from images
    """
    
    def __init__(self):
        self.model = None
        self.transform = None
        self.class_names = self._load_class_names()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self._initialize_model()
    
    def _load_class_names(self) -> List[str]:
        """Load furniture category class names"""
        # Define furniture categories that our model can recognize
        return [
            'chair', 'table', 'sofa', 'bed', 'desk', 'dresser', 'bookshelf',
            'nightstand', 'dining_table', 'coffee_table', 'cabinet', 'stool',
            'armchair', 'ottoman', 'bench', 'wardrobe', 'lamp', 'mirror',
            'tv_stand', 'sideboard'
        ]
    
    def _initialize_model(self):
        """Initialize the ResNet18 model for furniture classification"""
        try:
            # Load pre-trained ResNet18
            self.model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
            
            # Modify the final layer for furniture classification
            num_classes = len(self.class_names)
            self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
            
            # Set model to evaluation mode (we'll use pre-trained features)
            self.model.eval()
            self.model.to(self.device)
            
            # Define image preprocessing transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            print(f"Computer Vision model initialized successfully on {self.device}")
            
            # Since we don't have a trained model, we'll use feature-based classification
            self._use_feature_based_classification = True
            
        except Exception as e:
            print(f"Error initializing CV model: {str(e)}")
            self.model = None
            self._use_feature_based_classification = True
    
    def classify_furniture(self, image_data: bytes) -> Dict[str, Any]:
        """
        Classify furniture type from image data
        """
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Preprocess image
            if self.transform:
                image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            else:
                # Fallback preprocessing
                image_tensor = self._fallback_preprocess(image)
            
            # Classify image
            if self.model and not self._use_feature_based_classification:
                # Use trained model (if available)
                classification = self._classify_with_model(image_tensor)
            else:
                # Use feature-based classification as fallback
                classification = self._classify_with_features(image, image_tensor)
            
            return classification
            
        except Exception as e:
            print(f"Error classifying image: {str(e)}")
            return self._get_default_classification()
    
    def _classify_with_model(self, image_tensor: torch.Tensor) -> Dict[str, Any]:
        """Classify using the trained model"""
        try:
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                top_prob, top_class = torch.max(probabilities, 1)
                
                # Get top 3 predictions
                top_probs, top_classes = torch.topk(probabilities, 3)
                
                results = []
                for i in range(3):
                    class_idx = top_classes[0][i].item()
                    confidence = top_probs[0][i].item()
                    class_name = self.class_names[class_idx] if class_idx < len(self.class_names) else "unknown"
                    
                    results.append({
                        "category": class_name,
                        "confidence": float(confidence),
                        "rank": i + 1
                    })
                
                return {
                    "primary_category": results[0]["category"],
                    "confidence": results[0]["confidence"],
                    "all_predictions": results,
                    "method": "neural_network"
                }
                
        except Exception as e:
            print(f"Error in model classification: {str(e)}")
            return self._get_default_classification()
    
    def _classify_with_features(self, image: Image.Image, image_tensor: torch.Tensor) -> Dict[str, Any]:
        """
        Feature-based classification using image analysis
        This is a simplified approach for demonstration
        """
        try:
            # Analyze image properties
            width, height = image.size
            aspect_ratio = width / height if height > 0 else 1.0
            
            # Convert to numpy for analysis
            image_array = np.array(image)
            
            # Basic color analysis
            avg_color = np.mean(image_array, axis=(0, 1))
            brightness = np.mean(avg_color)
            
            # Simple heuristic classification based on image properties
            predictions = []
            
            # Aspect ratio based classification
            if 0.8 <= aspect_ratio <= 1.2:
                # Square-ish images might be chairs, stools, or decorative items
                predictions.append(("chair", 0.6))
                predictions.append(("stool", 0.4))
                predictions.append(("ottoman", 0.3))
            elif aspect_ratio > 1.5:
                # Wide images might be tables, sofas, or beds
                predictions.append(("table", 0.7))
                predictions.append(("sofa", 0.6))
                predictions.append(("bed", 0.4))
            elif aspect_ratio < 0.7:
                # Tall images might be bookcases, lamps, or cabinets
                predictions.append(("bookshelf", 0.7))
                predictions.append(("cabinet", 0.6))
                predictions.append(("lamp", 0.4))
            else:
                # Default predictions
                predictions.append(("table", 0.5))
                predictions.append(("chair", 0.4))
                predictions.append(("sofa", 0.3))
            
            # Brightness-based adjustments
            if brightness > 200:  # Very bright images
                predictions = [(cat, conf * 1.1) for cat, conf in predictions]
            elif brightness < 100:  # Dark images
                predictions = [(cat, conf * 0.9) for cat, conf in predictions]
            
            # Sort by confidence and normalize
            predictions.sort(key=lambda x: x[1], reverse=True)
            
            # Normalize confidences to sum to 1
            total_conf = sum(conf for _, conf in predictions[:3])
            if total_conf > 0:
                predictions = [(cat, conf/total_conf) for cat, conf in predictions[:3]]
            
            # Format results
            results = []
            for i, (category, confidence) in enumerate(predictions[:3]):
                results.append({
                    "category": category,
                    "confidence": min(float(confidence), 1.0),
                    "rank": i + 1
                })
            
            return {
                "primary_category": results[0]["category"],
                "confidence": results[0]["confidence"],
                "all_predictions": results,
                "method": "feature_analysis",
                "image_properties": {
                    "aspect_ratio": aspect_ratio,
                    "brightness": float(brightness),
                    "dimensions": [width, height]
                }
            }
            
        except Exception as e:
            print(f"Error in feature-based classification: {str(e)}")
            return self._get_default_classification()
    
    def _fallback_preprocess(self, image: Image.Image) -> torch.Tensor:
        """Fallback image preprocessing when transforms are not available"""
        try:
            # Resize image
            image = image.resize((224, 224))
            
            # Convert to tensor
            image_array = np.array(image) / 255.0
            image_tensor = torch.FloatTensor(image_array).permute(2, 0, 1).unsqueeze(0)
            
            return image_tensor.to(self.device)
            
        except Exception as e:
            print(f"Error in fallback preprocessing: {str(e)}")
            # Return a dummy tensor
            return torch.zeros(1, 3, 224, 224).to(self.device)
    
    def _get_default_classification(self) -> Dict[str, Any]:
        """Return default classification when all methods fail"""
        return {
            "primary_category": "furniture",
            "confidence": 0.5,
            "all_predictions": [
                {"category": "furniture", "confidence": 0.5, "rank": 1},
                {"category": "table", "confidence": 0.3, "rank": 2},
                {"category": "chair", "confidence": 0.2, "rank": 3}
            ],
            "method": "default",
            "image_properties": {
                "aspect_ratio": 1.0,
                "brightness": 128.0,
                "dimensions": [224, 224]
            }
        }
    
    def extract_visual_features(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract visual features from furniture image for similarity matching
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract basic visual features
            features = {
                'dimensions': image.size,
                'aspect_ratio': image.size[0] / image.size[1] if image.size[1] > 0 else 1.0
            }
            
            # Color analysis
            image_array = np.array(image)
            features['dominant_colors'] = self._extract_dominant_colors(image_array)
            features['brightness'] = float(np.mean(image_array))
            features['contrast'] = float(np.std(image_array))
            
            # Texture analysis (simplified)
            features['texture_complexity'] = self._analyze_texture(image_array)
            
            # Extract CNN features if model is available
            if self.model and self.transform:
                features['cnn_features'] = self._extract_cnn_features(image)
            
            return features
            
        except Exception as e:
            print(f"Error extracting visual features: {str(e)}")
            return {'dimensions': [224, 224], 'aspect_ratio': 1.0}
    
    def _extract_dominant_colors(self, image_array: np.ndarray, num_colors: int = 3) -> List[List[int]]:
        """Extract dominant colors from image"""
        try:
            # Reshape image for clustering
            pixels = image_array.reshape(-1, 3)
            
            # Simple method: divide RGB space and find most common ranges
            # This is a simplified approach without proper clustering
            colors = []
            for i in range(num_colors):
                # Calculate mean color in different regions
                start_idx = i * len(pixels) // num_colors
                end_idx = (i + 1) * len(pixels) // num_colors
                mean_color = np.mean(pixels[start_idx:end_idx], axis=0)
                colors.append(mean_color.astype(int).tolist())
            
            return colors
            
        except Exception as e:
            print(f"Error extracting dominant colors: {str(e)}")
            return [[128, 128, 128]]  # Default gray
    
    def _analyze_texture(self, image_array: np.ndarray) -> float:
        """Analyze texture complexity of the image"""
        try:
            # Convert to grayscale
            gray = np.mean(image_array, axis=2)
            
            # Calculate gradient magnitude as a simple texture measure
            grad_x = np.gradient(gray, axis=1)
            grad_y = np.gradient(gray, axis=0)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Return mean gradient magnitude as texture complexity
            return float(np.mean(gradient_magnitude))
            
        except Exception as e:
            print(f"Error analyzing texture: {str(e)}")
            return 0.0
    
    def _extract_cnn_features(self, image: Image.Image) -> List[float]:
        """Extract CNN features using the pre-trained model"""
        try:
            # Preprocess image
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Extract features from the model (before the final classification layer)
            with torch.no_grad():
                # Get features from the avgpool layer
                features = self.model.avgpool(self.model.layer4(
                    self.model.layer3(self.model.layer2(
                        self.model.layer1(self.model.maxpool(
                            self.model.relu(self.model.bn1(self.model.conv1(image_tensor)))
                        ))
                    ))
                ))
                
                # Flatten features
                features = features.view(features.size(0), -1)
                
                return features.cpu().numpy().flatten().tolist()
                
        except Exception as e:
            print(f"Error extracting CNN features: {str(e)}")
            return [0.0] * 512  # Return default feature vector
    
    def compare_images(self, image1_data: bytes, image2_data: bytes) -> Dict[str, Any]:
        """
        Compare two furniture images and return similarity metrics
        """
        try:
            features1 = self.extract_visual_features(image1_data)
            features2 = self.extract_visual_features(image2_data)
            
            # Calculate various similarity metrics
            similarities = {}
            
            # Aspect ratio similarity
            ar1 = features1.get('aspect_ratio', 1.0)
            ar2 = features2.get('aspect_ratio', 1.0)
            similarities['aspect_ratio'] = 1.0 - abs(ar1 - ar2) / max(ar1, ar2)
            
            # Brightness similarity
            b1 = features1.get('brightness', 128.0)
            b2 = features2.get('brightness', 128.0)
            similarities['brightness'] = 1.0 - abs(b1 - b2) / 255.0
            
            # Texture similarity
            t1 = features1.get('texture_complexity', 0.0)
            t2 = features2.get('texture_complexity', 0.0)
            max_texture = max(t1, t2) if max(t1, t2) > 0 else 1.0
            similarities['texture'] = 1.0 - abs(t1 - t2) / max_texture
            
            # Overall similarity (weighted average)
            overall_similarity = (
                0.3 * similarities['aspect_ratio'] +
                0.3 * similarities['brightness'] +
                0.4 * similarities['texture']
            )
            
            return {
                'overall_similarity': float(overall_similarity),
                'detailed_similarities': similarities,
                'features1': features1,
                'features2': features2
            }
            
        except Exception as e:
            print(f"Error comparing images: {str(e)}")
            return {'overall_similarity': 0.5, 'detailed_similarities': {}}
    
    def get_supported_categories(self) -> List[str]:
        """Return list of supported furniture categories"""
        return self.class_names.copy()
    
    def batch_classify(self, image_data_list: List[bytes]) -> List[Dict[str, Any]]:
        """
        Classify multiple images in batch for efficiency
        """
        results = []
        for image_data in image_data_list:
            result = self.classify_furniture(image_data)
            results.append(result)
        
        return results