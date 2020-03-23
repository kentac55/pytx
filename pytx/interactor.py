from abc import ABC, abstractmethod
from functools import wraps
from logging import Logger
from typing import Callable, ContextManager, Generic, TypeVar

from .req import Request
from .res import FailureResponse, Response, ResponseValue

# RequestObjectを抽象化したもの
_A = TypeVar("_A", bound=Request, contravariant=True)
# ResponseValueを抽象化したもの
_B = TypeVar("_B", bound=ResponseValue, covariant=True)


class _InputPort(ABC):
    # yieldされる値は使わないのでNoneで良い
    ctx: ContextManager[None]
    logger: Logger


class InputPort(_InputPort, Generic[_A, _B]):
    """Interactorの基底クラス"""

    @abstractmethod
    def exec(self, req: _A) -> Response[_B]:
        """UseCaseInteractorのCommand Method

        Notes:
            おそらく引数の型は_Aを上界に持つAと_Bを上界に持つBみたいなのを
            指定するべき？だがTypeVarはboundにgeneric typeを取ることができない
            >>> A = TypeVar("A", bound=_A)
            >>> B = TypeVar("B", bound=_B)
            とりあえずこれでも動く
        """


# generic部分と分離したclassをboundに指定する
_I = TypeVar("_I", bound=_InputPort, contravariant=True)
# この型が頻出するのでaliasにしておく
_F = Callable[[_I, _A], Response[_B]]


def tx(f: _F) -> _F:
    @wraps(f)
    def _(cls: _I, req: _A, *args, **kwargs) -> Response[_B]:
        try:
            with cls.ctx:
                return f(cls, req, *args, **kwargs)
        except Exception as e:
            cls.logger.exception(e)
            return FailureResponse(e, req.request_id)

    return _
