import json
import re
import time
from dataclasses import dataclass
from typing import List

import requests


@dataclass(frozen=True)
class DeepSeekClient:
    base_url: str
    api_key: str
    model: str
    proxy: str = ""

    def translate_batch(self, texts: List[str], target_language: str) -> List[str]:
        if not self.base_url:
            raise ValueError("DEEPSEEK_BASE_URL is required")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required")

        url = self.base_url.rstrip("/") + "/chat/completions"
        
        proxies = None
        if self.proxy:
            proxies = {"http": self.proxy, "https": self.proxy}
        
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional subtitle translator. Return only strict JSON.",
                        },
                        {
                            "role": "user",
                            "content": (
                                "Translate each item to the target language. "
                                "Return a JSON array of strings with the same length and order as the input.\n\n"
                                f"Target language: {target_language}\n\n"
                                "Input JSON:\n" + json.dumps(texts, ensure_ascii=False)
                            ),
                        },
                    ],
                    "temperature": 0.2,
                }

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }

                resp = requests.post(url, headers=headers, json=payload, timeout=120, proxies=proxies)
                resp.raise_for_status()
                data = resp.json()
                
                try:
                    content = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError) as e:
                    raise ValueError(f"Unexpected API response structure: {data}") from e

                content = self._clean_json_content(content)

                try:
                    parsed = json.loads(content)
                except json.JSONDecodeError as e:
                    # Provide a snippet of content for debugging
                    snippet = content[:200] + "..." if len(content) > 200 else content
                    raise ValueError(f"DeepSeek response is not valid JSON: {snippet}") from e

                if not isinstance(parsed, list) or len(parsed) != len(texts):
                    raise ValueError("DeepSeek response must be a JSON array with the same length as input")

                out: List[str] = []
                for item in parsed:
                    if not isinstance(item, str):
                        out.append(str(item))
                    else:
                        out.append(item)

                return out

            except (requests.RequestException, ValueError) as e:
                # If it's the last attempt, raise the exception
                if attempt == max_retries - 1:
                    raise e
                
                # Log warning (print to console for now) and sleep
                print(f"[DeepSeekClient] Batch translation failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying...")
                time.sleep(base_delay * (attempt + 1))

        raise RuntimeError("Translation failed after retries")

    @staticmethod
    def _clean_json_content(content: str) -> str:
        # Remove ```json ... ``` or ``` ... ``` wrappers if present
        pattern = r"^```(?:json)?\s*(.*?)\s*```$"
        match = re.search(pattern, content.strip(), re.DOTALL)
        if match:
            return match.group(1)
        return content.strip()
