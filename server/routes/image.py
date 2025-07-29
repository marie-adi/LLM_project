from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.tools.generate_image import generate_image
from loguru import logger
import base64
from io import BytesIO
from fastapi.responses import Response

router = APIRouter(prefix="/images", tags=["Image Generation"])

class ImageRequest(BaseModel):
    prompt: str
    output_format: str = "jpeg"  # Can be jpeg/png

@router.post("/generate", summary="Generate image from text prompt")
async def create_image(request: ImageRequest):
    try:
        logger.info(f"Generating image for prompt: {request.prompt}")
        
        # Generate the image (returns base64 string)
        image_data = generate_image(request.prompt)
        
        # Decode the base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Return as image response
        return Response(
            content=image_bytes,
            media_type=f"image/{request.output_format}"
        )
        
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )