from io import BytesIO
from typing import Iterable

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from Backend.app.drafting.context_state.states import ImageState
IMAGE_ALLOWED_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}


async def validate_image_format(
    file: UploadFile,
    *,
    allowed_formats: Iterable[str],
) -> None:
    """
    Validate the actual image format using Pillow.
    Example formats: JPEG, PNG, WEBP.
    """

    data = await file.read()
    await file.seek(0)

    try:
        with Image.open(BytesIO(data)) as img:
            image_format = img.format.upper()

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file.",
        )

    allowed = {fmt.upper() for fmt in allowed_formats}

    if image_format not in allowed:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported image format '{image_format}'. "
                f"Allowed formats: {', '.join(sorted(allowed))}."
            ),
        )


async def validate_image_pixels(
    file: UploadFile,
    *,
    max_pixels: int,
) -> None:
    """
    Prevent decompression bomb attacks by limiting the total number of pixels.
    """

    data = await file.read()
    await file.seek(0)

    try:
        with Image.open(BytesIO(data)) as img:
            width, height = img.size

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file.",
        )

    pixels = width * height

    if pixels > max_pixels:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Image contains {pixels:,} pixels. "
                f"Maximum allowed is {max_pixels:,}."
            ),
        )


async def validate_exif(
    file: UploadFile,
    *,
    allow_exif: bool = False,
) -> None:
    """
    Validate whether EXIF metadata is present.

    Useful for rejecting images containing GPS or camera metadata.
    """

    data = await file.read()
    await file.seek(0)

    try:
        with Image.open(BytesIO(data)) as img:
            exif = img.getexif()

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file.",
        )

    if exif and not allow_exif:
        raise HTTPException(
            status_code=400,
            detail="Image contains EXIF metadata which is not allowed.",
        )
        


IMAGE_MAX_PIXELS = 25_000_000


async def validate_image(
    state:UploadFile
) -> None:
    """
    Runs all image validations.
    """
    file=state

    await validate_image_format(
        file=file,
        allowed_formats=IMAGE_ALLOWED_FORMATS,
    )

    await validate_image_pixels(
        file=file,
        max_pixels=IMAGE_MAX_PIXELS,
    )

    await validate_exif(
        file=file,
        allow_exif=False,
    )