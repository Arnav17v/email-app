"""
Script to list all available Gemini models for your API key
Run this to see which models you can use
"""
from google import genai
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    print("❌ GEMINI_API_KEY not found in .env file")
    exit(1)

print("🔍 Checking available Gemini models...\n")

try:
    client = genai.Client()
    
    # List all available models
    models = client.models.list()
    
    print("✅ Available models for your API key:\n")
    print("-" * 80)
    
    for model in models:
        print(f"📦 Model: {model.name}")
        if hasattr(model, 'display_name'):
            print(f"   Display Name: {model.display_name}")
        if hasattr(model, 'description'):
            print(f"   Description: {model.description[:100]}...")
        print("-" * 80)
    
    print("\n💡 Recommended models for free tier:")
    print("   - gemini-1.5-flash-latest")
    print("   - gemini-1.5-pro-latest")
    print("   - gemini-1.5-flash")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\n💡 Try these model names:")
    print("   - gemini-1.5-flash-latest")
    print("   - gemini-1.5-pro-latest")
    print("   - gemini-1.5-flash")
    print("   - gemini-1.5-pro")

