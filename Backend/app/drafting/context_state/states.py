from typing import Any

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field
from PIL import Image


# ==========================================================
# IMAGE STATE
# ==========================================================

class ImageState(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    upload_file: UploadFile

    image_bytes: bytes | None = None
    pil_image: Image.Image | None = None

    description: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    embedding: list[float] | None = None


# ==========================================================
# PDF STATE
# ==========================================================

class PDFState(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    upload_file: UploadFile

    text: str = ""

    summary: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    embedding: list[float] | None = None


class DocumentState(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    upload_file: UploadFile

    text: str = ""

    summary: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    embedding: list[float] | None = None

# ==========================================================
# REQUEST STATE
# ==========================================================

class RequestState(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    topic: str

    platform: str

    additional_context: str | None = None


# ==========================================================
# PARSED DATA STATE
# ==========================================================

class ParsedState(BaseModel):

    image_descriptions: list[str] = Field(default_factory=list)

    pdf_contents: list[str] = Field(default_factory=list)


# ==========================================================
# AI STATE
# ==========================================================

class AIState(BaseModel):

    combined_context: str = ""

    prompt: str = ""

    retrieved_context: str = ""


# ==========================================================
# OUTPUT STATE
# ==========================================================

class OutputState(BaseModel):

    draft: str = ""

    reviewed_draft: str = ""

    final_output: str = ""


# ==========================================================
# RUNTIME STATE
# ==========================================================

class RuntimeState(BaseModel):

    warnings: list[str] = Field(default_factory=list)

    errors: list[str] = Field(default_factory=list)


# ==========================================================
# MAIN PIPELINE STATE
# ==========================================================

class IngestionContext(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    request: RequestState

    images: list[ImageState] = Field(default_factory=list)

    pdfs: list[PDFState] = Field(default_factory=list)
    
    Documents:list[DocumentState] = Field(default_factory=list)

    parsed: ParsedState = Field(default_factory=ParsedState)

    ai: AIState = Field(default_factory=AIState)

    output: OutputState = Field(default_factory=OutputState)

    runtime: RuntimeState = Field(default_factory=RuntimeState)