from dataclasses import dataclass
from typing import Optional, final


@dataclass(frozen=True)
class Request:
    """RequestObjectの基底クラス

    例えばx_request_idをここに渡してapplication logicの中のlog出力に使う
    """

    request_id: Optional[str]


@final
@dataclass(frozen=True)
class IdRequest(Request):
    """Idのみをparamに持つRequestObject

    RESTで例えると `GET /users/{user_id}` とか
    """

    id: str


@final
@dataclass(frozen=True)
class NoneRequest(Request):
    """paramに何も持たないRequestObject

    RESTっぽくない `POST /switch/on` みたいな怪しいときに
    """
