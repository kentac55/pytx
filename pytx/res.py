"""Response Objectを定義したmodule

Response = SuccessResponse | FailureResponse
SuccessResponse = SuccessType & ResponseValue
と考えている
"""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Generic, Iterable, Literal, Optional, TypeVar, Union, final

_S = Literal["Ok", "Created", "Accepted", "NoContent"]


class ResponseValue(ABC):
    """ResponseValueの抽象クラス"""


_T = TypeVar("_T", bound=ResponseValue, contravariant=True)


@final
@dataclass(frozen=True)
class NoneResponseValue(ResponseValue):
    """空のresponse value"""


@final
@dataclass(frozen=True)
class QueryResponseValue(Generic[_T], ResponseValue):
    """query用response value"""

    values: Iterable[_T]


@final
class SuccessResponse(Generic[_T]):
    """アプリケーションロジックの成功を表現するResponseObject"""

    type_: _S
    value: _T
    req_id: Optional[str]
    ok = True

    def __init__(self, type_: _S, value: _T, req_id: Optional[str]) -> None:
        self.type_ = type_
        self.value = value
        self.request_id = req_id

    @classmethod
    def create_ok_response(
        cls, value: _T, req_id: Optional[str]
    ) -> SuccessResponse[_T]:
        return cls("Ok", value, req_id)

    @classmethod
    def create_created_response(
        cls, value: _T, req_id: Optional[str]
    ) -> SuccessResponse[_T]:
        return cls("Created", value, req_id)

    @classmethod
    def create_accepted_response(
        cls, value: _T, req_id: Optional[str]
    ) -> SuccessResponse[_T]:
        return cls("Accepted", value, req_id)

    @classmethod
    def create_no_content_response(
        cls, req_id: Optional[str]
    ) -> SuccessResponse[NoneResponseValue]:
        return cls("NoContent", NoneResponseValue(), req_id)


@final
class FailureResponse:
    """アプリケーションロジックの成功を表現するResponseObject

    扱いやすくするためにgeneric型にしない
    """

    e: Exception
    request_id: Optional[str]
    ok = False

    def __init__(self, e: Exception, req_id: Optional[str]) -> None:
        self.e = e
        self.request_id = req_id


Response = Union[SuccessResponse[_T], FailureResponse]
