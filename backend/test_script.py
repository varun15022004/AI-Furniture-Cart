"""
Test script to validate the backend API endpoints
"""
import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None, params=None):
    """Test an API endpoint and return the response"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"\n{'='*50}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and 'data' in result:
                print(f"Data count: {len(result.get('data', []))}")
            print("✅ Success")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {BASE_URL}")
        print("Make sure the backend server is running with: uvicorn main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return None

def main():
    print("🚀 Testing Furniture E-commerce Backend API")
    print(f"Testing against: {BASE_URL}")
    
    # Test basic endpoints
    test_endpoint("/")
    test_endpoint("/health")
    
    # Test products endpoints
    products = test_endpoint("/api/products")
    test_endpoint("/api/products", params={"limit": 5})
    test_endpoint("/api/products", params={"category": "Chair"})
    test_endpoint("/api/products/search", params={"q": "chair"})
    
    # Test specific product if we have products
    if products and products.get('data'):
        product_id = products['data'][0].get('id')
        if product_id:
            test_endpoint(f"/api/products/{product_id}")
            test_endpoint(f"/api/products/{product_id}/recommendations")
    
    # Test analytics endpoints
    test_endpoint("/api/analytics/overview")
    test_endpoint("/api/analytics/categories")
    test_endpoint("/api/analytics/brands")
    test_endpoint("/api/analytics/price-distribution")
    
    # Test AI description generation
    test_endpoint("/api/ai/generate-description", method="POST", data={
        "product_name": "Modern Office Chair",
        "category": "Chair",
        "material": "Leather",
        "brand": "TestBrand",
        "price": "$299.99"
    })
    
    print(f"\n{'='*50}")
    print("🎉 Testing completed!")
    print("\nIf you see connection errors, make sure to start the backend server:")
    print("uvicorn main:app --reload")

if __name__ == "__main__":
    main()