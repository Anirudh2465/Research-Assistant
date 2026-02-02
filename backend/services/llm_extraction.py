import requests
import json
from backend.core.config import settings
from backend.core.logging import logger

class LLMExtractor:
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

    def _call_llm(self, messages, temperature=0.1):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            choice = resp.json()["choices"][0]["message"]["content"]
            return choice
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise e

    def extract_raw_concepts(self, text_chunk: str):
        system_prompt = (
            "You are extracting technical concepts from a research paper. "
            "Do NOT abstract. List ALL concrete concepts, methods, assumptions, datasets, and metrics. "
            "Return JSON only: {\"concepts\": [], \"methods\": [], \"assumptions\": [], \"limitations\": []}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Text:\n{text_chunk}"}
        ]
        response_text = self._call_llm(messages)
        # Naive json extraction - in prod usage, use a proper parser or guidance/outlines
        try:
            # Try to find JSON blob
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(response_text[start:end])
            return json.loads(response_text)
        except Exception:
            logger.warning("Failed to parse LLM JSON response")
            return {"concepts": [], "methods": [], "assumptions": [], "limitations": []}

    def abstract_concepts(self, raw_concepts: list):
        system_prompt = (
             "You are a senior researcher. Abstract ONLY high-level research concepts. "
             "Avoid generic math or ML terms. Prefer domain-specific abstractions. "
             "Return JSON: {\"high_level_concepts\": [{\"name\": \"...\", \"description\": \"...\", \"confidence\": 0.0-1.0}]}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Raw concepts:\n{json.dumps(raw_concepts)}"}
        ]
        response_text = self._call_llm(messages)
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(response_text[start:end])
            return json.loads(response_text)
        except Exception:
             return {"high_level_concepts": []}

llm_extractor = LLMExtractor()
