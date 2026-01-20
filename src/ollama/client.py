"""
HTTP client for Ollama API.

Provides low-level interface to Ollama's vision capabilities.
"""

import httpx
import logging
import time
from typing import Optional, Dict, Any, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    HTTP client for interacting with Ollama API.

    Attributes:
        base_url: Ollama API base URL
        model: Vision model name
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "ministral-3:8b",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama server URL
            model: Vision model to use
            timeout: Request timeout in seconds (0 or -1 to disable)
            max_retries: Maximum retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        # Convert 0 or -1 to None (disable timeout)
        self.timeout = None if timeout in (0, -1) else timeout
        self.max_retries = max_retries

    def check_availability(self) -> bool:
        """
        Check if Ollama server is available and model is pulled.

        Returns:
            True if Ollama is available and ready, False otherwise
        """
        try:
            # Check server
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                if response.status_code != 200:
                    logger.warning("Ollama server not responding")
                    return False

                # Check if model is available
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]

                # Check for exact match or partial match (e.g., "ministral-3:8b" or "ministral-3:latest")
                model_available = any(
                    self.model in model_name or model_name in self.model
                    for model_name in models
                )

                if not model_available:
                    logger.warning(f"Model '{self.model}' not found. Available: {models}")
                    return False

                logger.info(f"Ollama available with model: {self.model}")
                return True

        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False

    def generate_with_image(
        self,
        prompt: str,
        image_path: str,
        stream: bool = False
    ) -> Optional[str]:
        """
        Generate text response from image and prompt.

        Args:
            prompt: Text prompt for the model
            image_path: Path to image file
            stream: Whether to stream the response

        Returns:
            Generated text response, or None if failed

        Raises:
            FileNotFoundError: If image file doesn't exist
            httpx.TimeoutException: If request times out
        """
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Read and encode image as base64
        import base64
        with open(image_file, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Prepare request
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_data],
            "stream": stream
        }

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        f"{self.base_url}/api/generate",
                        json=payload
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return result.get('response', '').strip()
                    else:
                        logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                        return None

            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Timeout after {self.max_retries} attempts")
                    raise

            except Exception as e:
                logger.error(f"Ollama API error: {e}")
                return None

        return None

    def generate_text(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
        progress_callback: Optional[Callable[[str], None]] = None,
        stop_condition: Optional[Callable[[str], bool]] = None
    ) -> Optional[str]:
        """
        Generate text from prompt using Ollama.

        Args:
            prompt: Text prompt
            system: Optional system message
            temperature: Sampling temperature
            stream: Whether to stream the response
            progress_callback: Optional callback function(chunk: str) for streaming updates
            stop_condition: Optional callback(full_text) -> bool that returns True to stop generation early

        Returns:
            Generated text or None if failed
        """
        if not self.check_availability():
            logger.warning("Ollama not available")
            return None

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

        if system:
            payload["system"] = system

        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    if stream:
                        # Stream the response
                        full_response = ""
                        stopped_early = False
                        with client.stream(
                            "POST",
                            f"{self.base_url}/api/generate",
                            json=payload
                        ) as response:
                            response.raise_for_status()

                            import json as json_module
                            for line in response.iter_lines():
                                if line.strip():
                                    try:
                                        chunk_data = json_module.loads(line)
                                        chunk = chunk_data.get("response", "")
                                        if chunk:
                                            full_response += chunk
                                            if progress_callback:
                                                progress_callback(chunk)
                                            # Check stop condition
                                            if stop_condition and stop_condition(full_response):
                                                logger.info("Stop condition met, ending generation early")
                                                stopped_early = True
                                                break
                                    except json_module.JSONDecodeError:
                                        continue

                        return full_response
                    else:
                        # Non-streaming mode (original behavior)
                        response = client.post(
                            f"{self.base_url}/api/generate",
                            json=payload
                        )
                        response.raise_for_status()

                        result = response.json()
                        return result.get("response", "")

            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Timeout, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries exceeded")
                    return None
            except Exception as e:
                logger.error(f"Error generating text: {e}")
                return None

        return None

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current model.

        Returns:
            Model information dictionary, or None if failed
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    f"{self.base_url}/api/show",
                    json={"name": self.model}
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return None

        except Exception as e:
            logger.debug(f"Failed to get model info: {e}")
            return None

    def get_context_length(self) -> int:
        """
        Get the model's context length (max tokens).

        Returns:
            Context length in tokens, or default of 8192 if unknown
        """
        model_info = self.get_model_info()
        if model_info:
            # Try to find context_length in model_info
            model_details = model_info.get('model_info', {})
            # Look for context_length key with different possible prefixes
            for key in model_details:
                if 'context_length' in key:
                    return model_details[key]
        # Default context length if we can't determine it
        return 8192

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).

        Uses ~4 characters per token as a rough estimate.
        This is conservative for most models.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 chars per token (conservative)
        return len(text) // 4
