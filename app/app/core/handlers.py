from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []

    for err in errors:
        loc = " -> ".join(str(loc) for loc in err["loc"])
        msg = err["msg"]

        # Customizing the 'folder_id' missing error
        if "folder_id" in loc and err["type"] == "missing":
            msg = "⚠️ The 'folder_id' field is required. Please provide a valid 24-character hex string."

        formatted_errors.append(
            {"field": loc, "message": msg, "error_type": err["type"]}
        )

    # Improved response structure
    response_content = {
        "status": "error",
        "code": 422,
        "path": str(request.url),
        "message": "Validation Failed",
        "errors": formatted_errors,
    }

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(response_content),
    )
