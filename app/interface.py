from http import HTTPStatus
from typing import Any

from pydantic import BaseModel


class XtrackingBaseResponse(BaseModel):
    code: int = HTTPStatus.CREATED
    message: str = "Create a Record Success"
    data: Any | None = None
    extra: Any | None = None


class XtrackingErrorWebResponse(XtrackingBaseResponse):
    code: int = HTTPStatus.BAD_REQUEST
    error: Any | None = None
    target: str = ''