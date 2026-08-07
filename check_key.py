import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GROQ_API_KEY")

if key:
    print(f"✅ Key found! It starts with: {key[:10]}...")
else:
    print("❌ Key NOT found. Your .env file is either missing or incorrectly formatted.")