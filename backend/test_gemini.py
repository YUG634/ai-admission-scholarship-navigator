import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No API key found in .env file")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

# Configure Gemini
genai.configure(api_key=api_key)

# List all available models
print("\n📋 Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  ✅ {model.name}")
        print(f"     Display: {model.display_name}")
        print(f"     Methods: {model.supported_generation_methods}")
        print()

# Try each model
test_models = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-pro",
    "gemini-1.0-pro",
    "gemini-2.0-flash-exp",
]

print("\n🧪 Testing models:")
for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Hello' in one word")
        print(f"  ✅ {model_name}: {response.text[:50]}")
    except Exception as e:
        print(f"  ❌ {model_name}: {str(e)[:100]}")