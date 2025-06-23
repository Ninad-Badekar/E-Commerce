from fastapi import Request
from fastapi.responses import JSONResponse
import logging

async def log_errors(request:Request,call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.error(f"Unhandled exception : {e}")
        return JSONResponse(
            status_code=500,
            content={"detail":"Internal Servor Error"}
            )