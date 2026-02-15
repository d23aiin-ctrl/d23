"""
Image-to-image service for stylization.

Uses fal.ai API for cloud-based image transformation.
Falls back to local diffusers when available.
"""

import asyncio
import base64
import io
import logging
import os
from typing import Optional, Tuple

import httpx
from PIL import Image

logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "runwayml/stable-diffusion-v1-5"
FAL_IMG2IMG_MODEL = "fal-ai/flux/dev/image-to-image"


def _pick_device() -> Tuple[str, str]:
    try:
        import torch
        if torch.backends.mps.is_available():
            return "mps", "float16"
        return "cpu", "float32"
    except Exception:
        return "cpu", "float32"


class Img2ImgService:
    def __init__(self):
        self.model_id = os.getenv("LOCAL_IMG2IMG_MODEL", DEFAULT_MODEL_ID)
        self.device = os.getenv("LOCAL_IMG2IMG_DEVICE", "")
        self.fal_key = os.getenv("FAL_KEY", "")
        self._pipe = None
        self._client: Optional[httpx.AsyncClient] = None
        self._use_fal = bool(self.fal_key)

    def _load_pipeline(self):
        try:
            import torch
            from diffusers import StableDiffusionImg2ImgPipeline
        except Exception as exc:
            raise RuntimeError("diffusers/torch not installed") from exc

        device, dtype_name = _pick_device()
        if self.device:
            device = self.device
        dtype = torch.float16 if dtype_name == "float16" else torch.float32

        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
        )
        pipe = pipe.to(device)
        pipe.enable_attention_slicing()
        self._pipe = pipe
        logger.info(f"Img2img pipeline loaded on {device} using {self.model_id}")

    def _ensure_pipeline(self):
        if self._pipe is None:
            self._load_pipeline()

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client for fal.ai."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=120.0,
                headers={
                    "Authorization": f"Key {self.fal_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    def _prepare_image(self, image_bytes: bytes, max_size: int = 768) -> Image.Image:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = image.size
        if max(width, height) <= max_size:
            return image
        if width >= height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _generate_sync(
        self,
        image_bytes: bytes,
        prompt: str,
        strength: float,
        guidance_scale: float,
        num_steps: int,
    ) -> bytes:
        self._ensure_pipeline()
        init_image = self._prepare_image(image_bytes)
        result = self._pipe(
            prompt=prompt,
            image=init_image,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_steps,
        )
        image = result.images[0]
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()

    async def _generate_with_fal(
        self,
        image_bytes: bytes,
        prompt: str,
        strength: float,
        guidance_scale: float,
        num_steps: int,
    ) -> bytes:
        """Generate image using fal.ai API."""
        client = await self._get_client()

        # Prepare image as base64 data URL
        prepared_image = self._prepare_image(image_bytes)
        buffer = io.BytesIO()
        prepared_image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        image_url = f"data:image/png;base64,{image_base64}"

        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "strength": strength,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_steps,
            "image_size": "square_hd",
            "num_images": 1,
            "enable_safety_checker": False,
        }

        logger.info(f"Calling fal.ai img2img with prompt: {prompt[:50]}...")

        response = await client.post(
            f"https://fal.run/{FAL_IMG2IMG_MODEL}",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        images = data.get("images", [])
        if not images:
            raise RuntimeError("No images returned from fal.ai")

        # Download the generated image
        image_result_url = images[0].get("url")
        if not image_result_url:
            raise RuntimeError("No image URL in fal.ai response")

        logger.info(f"Downloading generated image from fal.ai...")
        image_response = await client.get(image_result_url)
        image_response.raise_for_status()

        return image_response.content

    async def generate(
        self,
        image_bytes: bytes,
        prompt: str,
        strength: float = 0.6,
        guidance_scale: float = 7.0,
        num_steps: int = 25,
    ) -> bytes:
        # Try fal.ai first if available
        if self._use_fal:
            try:
                return await self._generate_with_fal(
                    image_bytes, prompt, strength, guidance_scale, num_steps
                )
            except Exception as e:
                logger.warning(f"fal.ai img2img failed: {e}, trying local...")

        # Fall back to local diffusers
        return await asyncio.to_thread(
            self._generate_sync,
            image_bytes,
            prompt,
            strength,
            guidance_scale,
            num_steps,
        )


_img2img_service: Optional[Img2ImgService] = None


def get_img2img_service() -> Img2ImgService:
    global _img2img_service
    if _img2img_service is None:
        _img2img_service = Img2ImgService()
    return _img2img_service
