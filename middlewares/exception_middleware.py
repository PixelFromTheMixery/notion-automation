from utils.exception import NotionException
from utils.logger import logger

import json
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response
        except NotionException as exc:
            logger.error(exc)
            return JSONResponse(
                status_code = exc.status,
                content = {"Notion error": exc.message}
            )
        except Exception as exc:
            logger.error(exc)
            print(exc)
            raise HTTPException(
                status_code = 500,
                detail= {"Misc error": str(exc)}
            )