"""PPG error type and FastAPI rendering (docs/api-contracts.md section 5).

The real gateway answers failures with
`{"fingerprint": "<uuid>", "errors": [{"code": ..., "message": ...}]}`, and the
merchant's `PPGClient` surfaces `errors[].code`. The mock has to answer in the
same shape or error handling cannot be demonstrated against it.

This module lives outside `app/api/` on purpose: the service layer raises
`PPGError`, so depending on the API layer would invert the layering required by
docs/AGENTS.md section 3.
"""

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class PPGError(Exception):
    """A failure that must reach the client as a PPG error envelope."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        """Store the error code, message and HTTP status.

        Args:
            code: Machine-readable code, e.g. `purchase.invalid_state`.
            message: Human-readable explanation.
            status_code: HTTP status to answer with.
        """
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def ppg_error(code: str, message: str, status_code: int = 400) -> PPGError:
    """Build a `PPGError`.

    Args:
        code: Machine-readable code.
        message: Human-readable explanation.
        status_code: HTTP status to answer with.

    Returns:
        PPGError: The exception to raise.
    """
    return PPGError(code=code, message=message, status_code=status_code)


def _envelope(errors: list[dict[str, str]]) -> dict[str, Any]:
    """Wrap error items in the PPG envelope, stamping a correlation id.

    Args:
        errors: One or more `{"code", "message"}` items.

    Returns:
        dict[str, Any]: The response body.
    """
    return {"fingerprint": str(uuid.uuid4()), "errors": errors}


async def ppg_error_handler(request: Request, exc: PPGError) -> JSONResponse:
    """Render a service-layer `PPGError` as the PPG envelope.

    Args:
        request: Incoming request (unused, required by the handler signature).
        exc: The raised error.

    Returns:
        JSONResponse: PPG error envelope.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope([{"code": exc.code, "message": exc.message}]),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Render routing errors (401/404/...) as the PPG envelope too.

    A real gateway speaks this shape for every error it returns, so replacing
    FastAPI's default `{"detail": ...}` body is deliberate.

    Args:
        request: Incoming request (unused, required by the handler signature).
        exc: The raised exception.

    Returns:
        JSONResponse: PPG error envelope.
    """
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        errors = [detail]
    else:
        errors = [{"code": "unexpected.error", "message": str(detail)}]
    return JSONResponse(status_code=exc.status_code, content=_envelope(errors))


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Render a 422 body check in the PPG envelope, one item per problem.

    Args:
        request: Incoming request (unused, required by the handler signature).
        exc: The raised validation error.

    Returns:
        JSONResponse: PPG error envelope.
    """
    return JSONResponse(
        status_code=422,
        content=_envelope(
            [{"code": "request.invalid", "message": error["msg"]} for error in exc.errors()]
        ),
    )


def install_ppg_error_handlers(app: FastAPI) -> None:
    """Register the handlers above. Call once, at startup.

    `StarletteHTTPException` is registered as well as `HTTPException`: the 404
    for an unknown route is raised by the Starlette router using the *parent*
    class, and a handler registered for the FastAPI subclass does not catch it.

    Args:
        app: The FastAPI application.
    """
    app.add_exception_handler(PPGError, ppg_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
