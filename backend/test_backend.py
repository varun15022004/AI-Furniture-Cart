#!/usr/bin/env python3
"""
Simple test script for the FurniCraft backend
"""
import pandas as pd
import sys
import os

def load_and_process_products():
    """Load and process products like the main app does"""
    try:
        df = pd.read_csv("data/clean_products.csv")
        
        # Clean and normalize the data (same as main.py)
        df['price_num'] = df['price'].astype(str).str.replace('$', '').str.replace(',', '').str.replace('nan', '')
        df['price_num'] = pd.to_numeric(df['price_num'], errors='coerce')
        
        # Normalize column names
        df['categories_clean'] = df['categories']
        df['images_clean'] = df['images']
        df['material_norm'] = df['material']
        df['brand_norm'] = df['brand']
        df['color_norm'] = df['color']
        
        # Fill missing values
        df = df.fillna('')
        
        return df
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return None

def test_data_loading():
    """Test if we can load and process the CSV data"""
    try:
        df = load_and_process_products()
        if df is None:
            return False
            
        print(f"✅ Data loaded successfully: {len(df)} rows")
        print(f"✅ Columns: {list(df.columns)}")
        
        # Check for required columns
        required_cols = ['title', 'price_num', 'categories_clean']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"⚠️  Missing required columns: {missing_cols}")
            return False
        else:
            print("✅ All required columns present")
            
        # Test price conversion
        price_data = df['price_num'].dropna()
        if not price_data.empty:
            print(f"✅ Price statistics: min=${price_data.min():.2f}, max=${price_data.max():.2f}, mean=${price_data.mean():.2f}")
        else:
            print("⚠️ No valid price data found")
        
        # Show sample data
        print(f"✅ Sample processed data:")
        sample = df[['title', 'price', 'price_num', 'brand_norm']].head(2)
        print(sample)
        
        return True
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

def test_basic_import():
    """Test if we can import required modules"""
    try:
        import fastapi
        import uvicorn
        import pandas
        import numpy
        print("✅ All required modules available")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing FurniCraft Backend Components")
    print("=" * 50)
    
    # Test basic imports
    if not test_basic_import():
        sys.exit(1)
    
    # Test data loading
    if not test_data_loading():
        sys.exit(1)
    
    print("\n✅ All tests passed! Backend should work correctly.")