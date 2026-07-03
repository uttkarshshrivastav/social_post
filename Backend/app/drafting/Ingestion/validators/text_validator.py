from fastapi import HTTPException


min_length = 0,
max_lenght = 1000,

def validate_text_length(
    text: str | None,
    *,
    min_length: int | None = None,
    max_length: int | None = None,
) -> None:
    """
    Validate the length of a text field.
    """

    if text is None:
        return

    length = len(text)

    if min_length is not None and length < min_length:
        raise HTTPException(
            status_code=400,
            detail=f"{text} must contain at least {min_length} characters.",
        )

    if max_length is not None and length > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"{text} cannot exceed {max_length} characters.",
        )

def validate_encoding(
    text: str | None,
    *,
    encoding: str = "utf-8",
) -> None:
    """
    Ensure the text can be encoded using the specified encoding.
    """

    if text is None:
        return

    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        raise HTTPException(
            status_code=400,
            detail=f"{text} contains characters that cannot be encoded as {encoding}.",
        )


def validate_text(
    text=str,
    min_length = min_length,
    max_lenght = max_lenght,

)->None:
    validate_text_length(
        text=text,
        min_length = min_length,
        max_lenght = max_lenght,

    )
    validate_encoding(
        text=text
    )