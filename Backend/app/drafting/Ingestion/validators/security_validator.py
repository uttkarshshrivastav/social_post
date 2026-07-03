from io import BytesIO

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError
import zipfile



async def detect_zip_bomb(
    file: UploadFile,
    *,
    max_uncompressed_size: int = 500 * 1024 * 1024,   # 500 MB
    max_compression_ratio: float = 100.0,
    max_files: int = 1000,
) -> None:
    """
    Detect suspicious ZIP archives.
    """

    data = await file.read()
    await file.seek(0)

    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:

            infos = archive.infolist()

            if len(infos) > max_files:
                raise HTTPException(
                    400,
                    "ZIP archive contains too many files.",
                )

            total_compressed = 0
            total_uncompressed = 0

            for info in infos:
                total_compressed += info.compress_size
                total_uncompressed += info.file_size

            if total_uncompressed > max_uncompressed_size:
                raise HTTPException(
                    400,
                    "ZIP archive expands to an excessive size.",
                )

            if total_compressed > 0:
                ratio = total_uncompressed / total_compressed

                if ratio > max_compression_ratio:
                    raise HTTPException(
                        400,
                        "ZIP archive has a suspicious compression ratio.",
                    )

    except zipfile.BadZipFile:
        raise HTTPException(
            400,
            "Invalid ZIP archive.",
        )


async def detect_Document_bomb(
    file: UploadFile,
    *,
    max_pages: int = 1000,
    max_objects: int = 100_000,
) -> None:
    """
    Detect suspiciously large or complex PDFs.

    This is a heuristic, not a full PDF security scanner.
    """

    data = await file.read()
    await file.seek(0)

    try:
        reader = PdfReader(BytesIO(data))
    except PdfReadError:
        raise HTTPException(
            400,
            "Invalid PDF.",
        )

    if len(reader.pages) > max_pages:
        raise HTTPException(
            400,
            "PDF contains too many pages.",
        )

    object_count = 0

    try:
        for _ in reader.resolved_objects.values():
            object_count += 1
    except Exception:
        pass

    if object_count > max_objects:
        raise HTTPException(
            400,
            "PDF appears excessively complex.",
        )
        
async def security_validation(
    pdf:UploadFile,
    markdown:UploadFile
    
)->None:
    
    await detect_zip_bomb(
     file=pdf   
    )
    await detect_zip_bomb(
     file=markdown   
    )
    await detect_Document_bomb(
        file=pdf
    )
    
    await detect_Document_bomb(
        file=markdown
    )
    