import json
import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings

logger = logging.getLogger("shreyas_portfolio")
logging.basicConfig(level=logging.INFO, format="%(message)s")

MAX_GLOBAL_BODY_BYTES = 1_048_576  # 1 MB
ROUTE_BODY_CAPS: dict[str, int] = {
    f"{settings.API_V1_PREFIX}/agent/chat": 4096,
    f"{settings.API_V1_PREFIX}/contact": 16384,
    f"{settings.API_V1_PREFIX}/public/contact-reveal": 2048,
}

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url=None,
)

# Layer 3: Strict CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID", "X-Turnstile-Token"],
    allow_credentials=False,
)


def _apply_security_headers(response: JSONResponse | object, request_id: str) -> None:
    headers = getattr(response, "headers", None)
    if headers is None:
        return
    headers["X-Request-ID"] = request_id
    headers["X-Content-Type-Options"] = "nosniff"
    headers["X-Frame-Options"] = "DENY"
    headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    headers["Permissions-Policy"] = (
        "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
        "microphone=(), payment=(), usb=()"
    )
    headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    )


# Layer 1, 2, & 4: Request ID, PII-redacted logging, Payload Cap, & OWASP Security Headers
@app.middleware("http")
async def security_perimeter_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    max_bytes = ROUTE_BODY_CAPS.get(request.url.path, MAX_GLOBAL_BODY_BYTES)
    content_length = request.headers.get("Content-Length")
    if content_length is not None:
        try:
            if int(content_length) > max_bytes:
                resp = JSONResponse(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    content={
                        "error_code": "PAYLOAD_TOO_LARGE",
                        "message": f"Request body exceeds maximum allowed size of {max_bytes} bytes.",
                        "request_id": request_id,
                    },
                )
                _apply_security_headers(resp, request_id)
                return resp
        except ValueError:
            pass

    if request.method in {"POST", "PUT", "PATCH"}:
        body = await request.body()
        if len(body) > max_bytes:
            resp = JSONResponse(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                content={
                    "error_code": "PAYLOAD_TOO_LARGE",
                    "message": f"Request body exceeds maximum allowed size of {max_bytes} bytes.",
                    "request_id": request_id,
                },
            )
            _apply_security_headers(resp, request_id)
            return resp

    response = await call_next(request)
    _apply_security_headers(response, request_id)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
            }
        )
    )
    return response


# Layer 5: Unified Error Envelopes (Zero Stack Traces)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    detail = exc.detail
    if isinstance(detail, dict):
        content = {
            "error_code": detail.get("error_code", f"HTTP_{exc.status_code}"),
            "message": detail.get("message", "Request failed."),
            "request_id": request_id,
        }
        if "retry_after_seconds" in detail:
            content["retry_after_seconds"] = detail.get("retry_after_seconds")
    else:
        content = {
            "error_code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
            "request_id": request_id,
        }
    resp = JSONResponse(status_code=exc.status_code, content=content)
    _apply_security_headers(resp, request_id)
    return resp


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    resp = JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request payload failed schema validation.",
            "request_id": request_id,
        },
    )
    _apply_security_headers(resp, request_id)
    return resp


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(json.dumps({"request_id": request_id, "error": type(exc).__name__}))
    resp = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "request_id": request_id,
        },
    )
    _apply_security_headers(resp, request_id)
    return resp


app.include_router(api_router, prefix=settings.API_V1_PREFIX)

