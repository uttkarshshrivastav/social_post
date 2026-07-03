from fastapi import HTTPException, UploadFile
from typing import List
from pydantic import Literal


PlatformType = Literal[
    "instagram", 
    "linkedin", 
    "twitter", 
    "x", 
    "facebook", 
    "youtube", 
    "tiktok"
]



def validate_platform(
    platform: str,
    SUPPORTED_PLATFORMS=PlatformType,    
    ) -> None:
    """
    Validate that the requested platform is supported.
    """

    platform = platform.strip().lower()

    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported platform '{platform}'. "
                f"Supported platforms: {', '.join(sorted(SUPPORTED_PLATFORMS))}"
            ),
        )





def validate_prompt(
    topic: str,
    additional_context: str | None = None,
    *,
    max_topic_length: int = 200,
    max_context_length: int = 5000,
) -> None:
    """
    Validate the textual request.
    """

    topic = topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )

    if len(topic) > max_topic_length:
        raise HTTPException(
            status_code=400,
            detail=f"Topic cannot exceed {max_topic_length} characters.",
        )

    if additional_context is not None:
        additional_context = additional_context.strip()

        if len(additional_context) > max_context_length:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Additional context cannot exceed "
                    f"{max_context_length} characters."
                ),
            )


def validate_file_count(
    images: List[UploadFile],
    pdfs: List[UploadFile],
    markdowns:List[UploadFile],
    *,
    max_images: int = 5,
    max_pdfs: int = 5,
    max_markdowns: int = 5,
    max_total_files: int = 10,
) -> None:
    """
    Validate the number of uploaded files.
    """

    if len(images) > max_images:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_images} images are allowed.",
        )

    if len(pdfs) > max_pdfs:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_pdfs} PDFs are allowed.",
        )
    if len(markdowns) > max_pdfs:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_markdowns} PDFs are allowed.",
        )

    total_files = len(images) + len(pdfs)

    if total_files > max_total_files:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_total_files} files can be uploaded.",
        )
        

async def validate_request (
    topic:str,
    platform:str,
    image:list[UploadFile],
    Pdf : List[UploadFile],
    markdown : list[UploadFile],
    additional_content:str,
)->None: 
    validate_platform(
        platform=platform,       
    )
    validate_prompt(
        topic=topic,
        additional_context=additional_content,
    )
    
    validate_file_count(
        images=image,
        pdfs=Pdf,
        markdowns=markdown
        
    )
