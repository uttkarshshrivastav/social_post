from bs4 import BeautifulSoup
from fastapi import HTTPException, UploadFile
import re
import unicodedata
from Backend.app.drafting.context_state.states import DocumentState


_ZERO_WIDTH_CHARS = {
    "\u200b",  # Zero Width Space
    "\u200c",  # Zero Width Non-Joiner
    "\u200d",  # Zero Width Joiner
    "\ufeff",  # BOM
}


max_character=10000,


async def validate_encoding(
    file: UploadFile,
    *,
    max_characters: int | None = None,
) -> str:
    """
    Validate that the uploaded file is a valid UTF-8 Markdown document.

    Returns:
        The decoded Markdown text.
    """

    data = await file.read()
    await file.seek(0)

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            400,
            "Markdown file must be UTF-8 encoded.",
        )

    if not text.strip():
        raise HTTPException(
            400,
            "Markdown file is empty.",
        )

    if max_characters is not None and len(text) > max_characters:
        raise HTTPException(
            400,
            f"Markdown exceeds the maximum length of {max_characters:,} characters.",
        )

    return text


def strip_html(markdown: str) -> str:
    """
    Remove any embedded HTML from Markdown.

    Markdown itself is preserved.
    """

    soup = BeautifulSoup(markdown, "html.parser")
    return soup.get_text()




def sanitize_markdown(markdown: str) -> str:
    """
    Sanitize Markdown text before processing.

    Operations:
    - Normalize Unicode (NFC)
    - Normalize line endings
    - Remove zero-width characters
    - Replace tabs with four spaces
    - Remove trailing whitespace
    - Remove HTML comments
    - Collapse excessive blank lines
    - Strip leading/trailing whitespace
    """

    # Normalize Unicode
    markdown = unicodedata.normalize("NFC", markdown)

    # Normalize line endings
    markdown = markdown.replace("\r\n", "\n").replace("\r", "\n")

    # Remove zero-width characters
    for char in _ZERO_WIDTH_CHARS:
        markdown = markdown.replace(char, "")

    # Replace tabs with spaces
    markdown = markdown.replace("\t", "    ")

    # Remove trailing whitespace
    markdown = "\n".join(line.rstrip() for line in markdown.split("\n"))

    # Remove HTML comments
    markdown = re.sub(
        r"<!--.*?-->",
        "",
        markdown,
        flags=re.DOTALL,
    )

    # Collapse 3+ blank lines into 2
    markdown = re.sub(
        r"\n{3,}",
        "\n\n",
        markdown,
    )

    # Remove leading/trailing whitespace
    markdown = markdown.strip()

    return markdown


async def validate_markdown(
    file: UploadFile, 
    max_characters: int = max_character
) -> DocumentState:
    """
    Orchestrates the validation, HTML stripping, and sanitization of a Markdown file.
    Returns a populated DocumentState ready for the pipeline.
    """
    
    raw_text = await validate_encoding(file, max_characters=max_characters)
    
    
    no_html_text = strip_html(raw_text)
    
    clean_text = sanitize_markdown(no_html_text)
    
    return DocumentState(
        upload_file=file,
        mime_type="text/markdown",
        text=clean_text,
        metadata={
            "original_filename": file.filename,
            "processed_character_count": len(clean_text)
        }
    )