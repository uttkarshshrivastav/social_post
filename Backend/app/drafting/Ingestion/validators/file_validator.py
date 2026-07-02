import os
import re
from pathlib import Path

from fastapi import HTTPException, UploadFile

from Backend.app.drafting.context_state.request_state import ImageState, PDFState



IMAGE_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
PDF_MAX_SIZE = 20 * 1024 * 1024   # 20 MB

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PDF_EXTENSIONS = {".pdf"}

IMAGE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
}

PDF_MIME_TYPES = {
    "application/pdf",
}

MAGIC_BYTES = {
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/jpeg": b"\xff\xd8\xff",
    "application/pdf": b"%PDF",
}

INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1F]')



async def validate_size(
    file: UploadFile,
    max_size: int,
) -> None:

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"{file.filename} exceeds the maximum allowed size."
        )


async def validate_extension(
    file: UploadFile,
    expected_extensions: set[str],
) -> None:

    extension = Path(file.filename).suffix.lower()

    if extension not in expected_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{extension}'."
        )


def validate_mime_type(
    file: UploadFile,
    allowed_types: set[str],
) -> None:

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"MIME type '{file.content_type}' is not allowed."
        )


async def validate_magic_bytes(
    file: UploadFile,
) -> None:

    expected = MAGIC_BYTES.get(file.content_type)

    if expected is None:
        return

    header = await file.read(len(expected))
    await file.seek(0)

    if not header.startswith(expected):
        raise HTTPException(
            status_code=400,
            detail="File content does not match its MIME type."
        )


def validate_filename(
    filename: str,
) -> None:

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename cannot be empty."
        )

    if len(filename) > 255:
        raise HTTPException(
            status_code=400,
            detail="Filename is too long."
        )

    if INVALID_FILENAME.search(filename):
        raise HTTPException(
            status_code=400,
            detail="Filename contains invalid characters."
        )


# ==========================================================
# COMPOSITE VALIDATORS
# ==========================================================

async def validate_image(
    image: ImageState,
) -> None:

    file = image.upload_file

    validate_filename(file.filename)

    await validate_size(
        file=file,
        max_size=IMAGE_MAX_SIZE,
    )

    await validate_extension(
        file=file,
        expected_extensions=IMAGE_EXTENSIONS,
    )

    validate_mime_type(
        file=file,
        allowed_types=IMAGE_MIME_TYPES,
    )

    await validate_magic_bytes(file)


async def validate_pdf(
    pdf: PDFState,
) -> None:

    file = pdf.upload_file

    validate_filename(file.filename)

    await validate_size(
        file=file,
        max_size=PDF_MAX_SIZE,
    )

    await validate_extension(
        file=file,
        expected_extensions=PDF_EXTENSIONS,
    )

    validate_mime_type(
        file=file,
        allowed_types=PDF_MIME_TYPES,
    )

    await validate_magic_bytes(file)