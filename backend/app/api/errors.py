from fastapi import HTTPException


def api_error(
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, str]] | None = None,
) -> HTTPException:
    error = {"code": code, "message": message}
    if details:
        error["details"] = details
    return HTTPException(status_code=status_code, detail=error)
