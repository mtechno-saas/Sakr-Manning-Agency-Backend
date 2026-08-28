"""
OCR backends for image-based PDFs and DOCX images.

The ``OllamaOcrService`` calls a local Ollama vision model
(``glm-ocr:latest`` by default) over HTTP. It supports:

  * Single image OCR (used for embedded DOCX images).
  * Multi-page parallel OCR (used for scanned PDFs).

When the model is unavailable (Ollama down, model not pulled,
network error) the service returns an empty string and logs the
failure — never raises. The caller falls back to whatever was
already extracted (or returns an error to the user).
"""

import base64
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Sequence

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


# Standard prompt for the OCR model. Kept neutral so the same
# prompt works for CVs, certificates, and other documents.
DEFAULT_OCR_PROMPT = (
    "Extract all text from this image exactly as it appears. "
    "Preserve the original layout, line breaks, and structure. "
    "Do not summarize, interpret, or translate. "
    "Return only the raw text content."
)


class OllamaOcrService:
    """OCR via a local Ollama vision model.

    Parameters
    ----------
    host : str, optional
        Base URL of the Ollama API (default: ``settings.OLLAMA_HOST``).
    model : str, optional
        Vision model name (default: ``settings.OCR_MODEL``).
    timeout : int, optional
        Per-page request timeout in seconds.
    max_workers : int, optional
        Max parallel calls for multi-page OCR.
    """

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        max_workers: int | None = None,
    ):
        self.host = (
            host
            or getattr(settings, "OLLAMA_HOST", "http://127.0.0.1:11434")
        ).rstrip("/")
        self.model = (
            model
            or getattr(settings, "OCR_MODEL", "glm-ocr:latest")
        )
        self.timeout = timeout or int(
            getattr(settings, "OCR_TIMEOUT_SECONDS", 60)
        )
        self.max_workers = max_workers or int(
            getattr(settings, "OCR_PARALLEL_WORKERS", 4)
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check if Ollama is reachable AND the configured model is
        loaded. Returns False on any error — never raises."""
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=5)
            if r.status_code != 200:
                logger.warning(
                    "Ollama tags endpoint returned HTTP %s from %s",
                    r.status_code, self.host,
                )
                return False
            data = r.json()
            model_root = self.model.split(":", 1)[0]
            return any(
                m.get("name", "").startswith(model_root)
                for m in data.get("models", [])
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Ollama OCR availability check failed (%s): %r",
                self.host, exc,
            )
            return False

    def ocr_image(self, image_bytes: bytes, prompt: str | None = None) -> str:
        """OCR a single image. Returns extracted text or empty string."""
        if not image_bytes:
            return ""
        try:
            b64 = base64.b64encode(image_bytes).decode("ascii")
            payload = {
                "model": self.model,
                "prompt": prompt or DEFAULT_OCR_PROMPT,
                "images": [b64],
                "stream": False,
            }
            r = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            r.raise_for_status()
            text = (r.json().get("response") or "").strip()
            logger.info(
                "OllamaOCR[%s]: extracted %d chars from %d-byte image",
                self.model, len(text), len(image_bytes),
            )
            return text
        except Exception as exc:  # noqa: BLE001
            logger.warning("OllamaOCR failed: %r", exc)
            return ""

    def ocr_pages(
        self,
        page_images: Sequence[bytes],
        prompt: str | None = None,
    ) -> List[str]:
        """OCR multiple page images in parallel. Returns a list with
        one entry per input image (empty string for failed pages)."""
        if not page_images:
            return []
        # Don't spawn more workers than pages
        workers = max(1, min(self.max_workers, len(page_images)))
        results: list[str] = [""] * len(page_images)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_to_idx = {
                ex.submit(
                    self.ocr_image, img_bytes, prompt
                ): idx
                for idx, img_bytes in enumerate(page_images)
            }
            for fut in as_completed(future_to_idx):
                idx = future_to_idx[fut]
                try:
                    results[idx] = fut.result() or ""
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "OllamaOCR page %d raised: %r", idx + 1, exc,
                    )
                    results[idx] = ""
        return results

    def ocr_pages_combined(
        self,
        page_images: Sequence[bytes],
        prompt: str | None = None,
        separator: str = "\n\n",
    ) -> str:
        """OCR multiple pages and join into a single string. Order
        matches the input order. Returns empty string if all pages
        failed."""
        if not page_images:
            return ""
        results = self.ocr_pages(page_images, prompt=prompt)
        return separator.join(t for t in results if t)
