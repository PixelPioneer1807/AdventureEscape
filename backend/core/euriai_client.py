import os
import time
import logging
from typing import Any, Dict, Optional


try:
    import requests
except ImportError as e:
    raise RuntimeError("The 'requests' package is required. Install with: pip install requests") from e


log = logging.getLogger("app.story")



class EuriaiResponse:
    """Minimal response exposing `.content` (assistant JSON string) and `.raw` (full envelope)."""
    def __init__(self, content: str, raw: Dict[str, Any] | None = None):
        self.content = content
        self.raw = raw or {}



class EuriaiChat:
    """
    Minimal Euriai chat client with `.invoke(input)` returning EuriaiResponse(content=assistant_message_content).
    """
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1400,
        timeout: int = 30,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("EURI_API_KEY")
        self.base_url = (base_url or os.getenv("EURI_BASE_URL") or "https://api.euron.one").rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout


    def _build_prompt_text(self, prompt_obj: Any) -> str:
        if hasattr(prompt_obj, "to_string"):
            return prompt_obj.to_string()
        if hasattr(prompt_obj, "messages"):
            parts = []
            for m in getattr(prompt_obj, "messages", []):
                parts.append(getattr(m, "content", str(m)))
            return "\n".join(parts)
        return str(prompt_obj)


    def invoke(self, prompt_obj: Any) -> EuriaiResponse:
        if not self.api_key:
            raise RuntimeError("EURI_API_KEY not set. Add it to .env before generating.")


        text = self._build_prompt_text(prompt_obj)


        base = self.base_url.rstrip("/")
        endpoint = f"{base}/api/v1/euri/chat/completions"


        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


        payload = {
            "messages": [
                {"role": "system", "content": "Return ONLY one valid JSON object matching the schema. No prose or code fences."},
                {"role": "user", "content": text},
            ],
            "model": self.model or "gpt-4.1-nano",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            # If unsupported, server ignores this; harmless.
            "response_format": {"type": "json_object"},
        }


        try:
            start = time.time()
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
            latency_ms = int((time.time() - start) * 1000)
        except Exception as e:
            raise RuntimeError(f"Euriai HTTP error: {e}")


        status = resp.status_code
        try:
            body_text = resp.text or ""
        except Exception:
            try:
                body_text = resp.content.decode("utf-8", errors="ignore")
            except Exception:
                body_text = ""


        log.debug("Euriai HTTP status=%s url=%s", status, endpoint)
        log.debug("Euriai response headers=%s", dict(resp.headers))
        log.debug("Euriai response body preview=%s", body_text[:500])


        if status >= 400:
            raise RuntimeError(f"Euriai error {status}: {body_text}")
        if not body_text.strip():
            raise RuntimeError("Euriai returned empty body; check API key, model, or endpoint.")


        data: Dict[str, Any] = {}
        try:
            data = resp.json()
        except Exception:
            # Not JSON; return raw text so upstream can attempt extraction
            return EuriaiResponse(content=body_text, raw={"status": status, "latency_ms": latency_ms, "body": body_text})

        # 🔧 FIX: Handle Euriai "data" wrapper if present
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
            data = data["data"]
            log.debug("Extracted content from Euriai 'data' wrapper")

        # 🔧 FIX: Extract assistant content string from envelope
        content = ""
        
        # Handle choices array properly
        if isinstance(data, dict) and "choices" in data:
            choices = data["choices"]
            if isinstance(choices, list) and len(choices) > 0:
                # 🔧 FIX: Access first choice from LIST, not treat as dict
                first_choice = choices[0]
                if isinstance(first_choice, dict):
                    # Standard OpenAI/Euriai format
                    msg = first_choice.get("message", {})
                    if isinstance(msg, dict):
                        content = msg.get("content", "")
                    
                    # Fallback to choice-level content
                    if not content:
                        content = first_choice.get("text", "") or first_choice.get("content", "")
                        
        # Additional fallbacks for different response formats
        if not content and isinstance(data, dict):
            content = (
                data.get("output", "") or 
                data.get("text", "") or 
                data.get("content", "") or
                body_text
            )

        # Final fallback
        if not content:
            content = body_text

        log.debug("Extracted content length=%d preview=%s", len(content), content[:200])

        return EuriaiResponse(content=content, raw={"status": status, "latency_ms": latency_ms, **data})