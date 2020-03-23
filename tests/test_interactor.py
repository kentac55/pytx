from contextlib import contextmanager
from dataclasses import dataclass
from logging import Logger
from typing import Any, ContextManager, Iterator, final
from unittest.mock import MagicMock

from pytx import (
    FailureResponse,
    InputPort,
    Request,
    Response,
    ResponseValue,
    SuccessResponse,
    tx,
)


@contextmanager
def _ctx(mock) -> Iterator[None]:
    try:
        mock.open()
        yield None
        mock.commit()
    except Exception as e:
        mock.open.assert_called_once_with()
        mock.rollback()
        raise e
    finally:
        mock.open.assert_called_once_with()
        mock.close()


class _TestRepository:
    def __init__(self, mock) -> None:
        self.mock = mock

    def exec(self):
        self.mock.open.assert_called_once_with()
        return self.mock.query()


@final
@dataclass(frozen=True)
class _TestResponseValue(ResponseValue):
    v: Any


class _TestInteractor(InputPort[Request, _TestResponseValue]):
    def __init__(self, ctx: ContextManager[None], repo: _TestRepository):
        self.ctx = ctx
        self.logger = Logger(__name__)
        self.repo = repo

    @tx
    def exec(self, req: Request) -> Response[_TestResponseValue]:
        v = self.repo.exec()
        return SuccessResponse.create_ok_response(_TestResponseValue(v), req.request_id)


# def test_txはContextを管理できる():
def test_tx_should_manage_context():
    mock = MagicMock()
    mock.open.return_value = None
    mock.query.return_value = 1
    mock.commit.return_value = None
    mock.rollback.return_value = None
    mock.close.return_value = None

    repo = _TestRepository(mock)
    interactor = _TestInteractor(_ctx(mock), repo)
    req = Request(request_id=None)
    res = interactor.exec(req)

    assert isinstance(res, SuccessResponse) and res.value.v == 1
    mock.open.assert_called_once_with()
    mock.query.assert_called_once_with()
    mock.commit.assert_called_once_with()
    mock.rollback.assert_not_called()
    mock.close.assert_called_once_with()


# def test_txは例外発生時にFailureResponseを返す():
def test_tx_should_return_FailureResponse_with_raising_exception():
    mock = MagicMock()
    mock.open.return_value = None
    mock.query.side_effect = Exception("ERROR")
    mock.commit.return_value = None
    mock.rollback.return_value = None
    mock.close.return_value = None

    repo = _TestRepository(mock)
    interactor = _TestInteractor(_ctx(mock), repo)
    req = Request(request_id=None)
    res = interactor.exec(req)

    assert isinstance(res, FailureResponse)
    mock.open.assert_called_once_with()
    mock.query.assert_called_once_with()
    mock.commit.assert_not_called()
    mock.rollback.assert_called_once_with()
    mock.close.assert_called_once_with()
