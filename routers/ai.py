import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from security import get_current_user
from models import User
import time
from fastapi.responses import StreamingResponse



router = APIRouter(prefix="/ai", tags=["AI"])

XAI_API_KEY = os.getenv("XAI_API_KEY")


@router.post("/generate")
async def generate_nail_art(
    prompt: str,
    current_user: User = Depends(get_current_user)
):
    if not XAI_API_KEY:
        raise HTTPException(status_code=500, detail="XAI_API_KEY not set on server")

    full_prompt = f"""Close-up professional studio photograph of realistic human hands showing only nail art on the fingernails.

User request: {prompt}

**STRICT RULES - FOLLOW THESE EXACTLY:**
- Generate **nail art ONLY**. Nothing else.
- Do not show any objects being held, no props, no background elements.
- The only thing visible should be the hands and the nail art.
- If the user mentions a specific finger, apply the special design ONLY to that finger.

Highly detailed, clean commercial photography style, soft lighting, sharp focus, 8k resolution.
Strictly family-friendly and positive. No hate speech, politics, religion, explicit content, or violence."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.x.ai/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {XAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "grok-imagine-image",
                    "prompt": full_prompt,
                    "n": 1,
                },
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        image_url = data.get("data", [{}])[0].get("url")

        if not image_url:
            raise HTTPException(status_code=500, detail="No image returned from AI")

        return {"image_url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    import time
from fastapi.responses import StreamingResponse

@router.get("/download")
async def download_image(image_url: str):
    """Proxy endpoint to force image download (works on mobile too)"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Could not fetch image from source")

        filename = f"nail-art-{int(time.time())}.jpg"

        return StreamingResponse(
            iter([response.content]),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")