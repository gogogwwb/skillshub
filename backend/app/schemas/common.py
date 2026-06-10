from pydantic import BaseModel
from typing import Optional, Any


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PageResult(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int


class ResponseBase(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


def success_response(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def error_response(code: int = -1, message: str = "error", data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}
