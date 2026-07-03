from io import BytesIO

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from Backend.app.drafting.context_state.states import PDFState

min_pages=0
max_pages=5
max_file_size_mb=10


async def validate_pdf_pages(
    file: UploadFile,
    *,
    min_pages: int | None = None,
    max_pages: int | None = None,
) -> None:
    """
    Validate the number of pages in a PDF.
    """

    data = await file.read()
    await file.seek(0)

    try:
        reader = PdfReader(BytesIO(data))
    except PdfReadError:
        raise HTTPException(400, "Invalid PDF file.")

    page_count = len(reader.pages)

    if min_pages is not None and page_count < min_pages:
        raise HTTPException(
            400,
            f"PDF must contain at least {min_pages} pages.",
        )

    if max_pages is not None and page_count > max_pages:
        raise HTTPException(
            400,
            f"PDF cannot contain more than {max_pages} pages.",
        )


async def validate_pdf_encryption(
    file: UploadFile,
    *,
    allow_encrypted: bool = False,
) -> None:
    """
    Reject encrypted/password-protected PDFs.
    """

    data = await file.read()
    await file.seek(0)

    try:
        reader = PdfReader(BytesIO(data))
    except PdfReadError:
        raise HTTPException(400, "Invalid PDF file.")

    if reader.is_encrypted and not allow_encrypted:
        raise HTTPException(
            400,
            "Encrypted PDF files are not allowed.",
        )


async def validate_pdf_javascript(
    file: UploadFile,
    *,
    allow_javascript: bool = False,
) -> None:
    """
    Detect embedded JavaScript in a PDF.

    This is a basic security check.
    """

    data = await file.read()
    await file.seek(0)

    try:
        reader = PdfReader(BytesIO(data))
    except PdfReadError:
        raise HTTPException(400, "Invalid PDF file.")

    root = reader.trailer.get("/Root", {})

    has_js = False

    if "/Names" in root:
        names = root["/Names"]
        if "/JavaScript" in names:
            has_js = True

    if "/OpenAction" in root:
        has_js = True

    if has_js and not allow_javascript:
        raise HTTPException(
            400,
            "PDF contains embedded JavaScript or automatic actions.",
        )


async def validate_pdf_size(
    file: UploadFile,
    *,
    max_pages: int,
    max_file_size_mb: float,
) -> None:
    """
    Ensure the PDF is reasonable in both page count and file size.
    """

    data = await file.read()
    await file.seek(0)

    file_size_mb = len(data) / (1024 * 1024)

    if file_size_mb > max_file_size_mb:
        raise HTTPException(
            400,
            f"PDF size ({file_size_mb:.2f} MB) exceeds "
            f"the limit of {max_file_size_mb} MB.",
        )

    try:
        reader = PdfReader(BytesIO(data))
    except PdfReadError:
        raise HTTPException(400, "Invalid PDF file.")

    if len(reader.pages) > max_pages:
        raise HTTPException(
            400,
            f"PDF contains more than {max_pages} pages.",
        )
        
        
async def validate_pdf_specific(
    file:UploadFile,  
)->None:
    input_file = file.upload_file
    await validate_pdf_pages(
    input_file,
    min_pages,
    max_pages,
)
    await validate_pdf_encryption(
        input_file,
        False,
    )
    
    await validate_pdf_javascript(
        input_file,
        False,
        
    )
    
    await validate_pdf_size(
        input_file,
        max_pages,
        max_file_size_mb,
    )
    
    