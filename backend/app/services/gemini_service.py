import os
import json
import re
from typing import Dict, Any
from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=self.api_key)
        # ✅ CHANGE: Use gemini-2.5-flash (higher quota)
        self.model_name = "gemini-2.5-flash"
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", 0.3))
        self.max_tokens = int(os.getenv("AGENT_MAX_TOKENS", 2048))

    def generate_structured_response(self, prompt: str) -> Dict[str, Any]:
        try:
            print(f"📤 Sending to Gemini ({self.model_name})...")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            text = response.text
            if not text:
                print("⚠️ Empty response from Gemini")
                return {}

            # Remove markdown code fences
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

            start = text.find("{")
            end = text.rfind("}") + 1

            if start == -1 or end <= 0:
                print(f"⚠️ No valid JSON found in response")
                return {}

            json_str = text[start:end]
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r",\s*]", "]", json_str)

            result = json.loads(json_str)
            print(f"✅ Parsed JSON successfully")
            return result

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return {}

        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return {}