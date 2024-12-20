from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generator, cast

import httpx
from typing_extensions import Self

from iloveapi.auth import TokenAuth
from iloveapi.rest import Rest
from iloveapi.task import Task

if TYPE_CHECKING:
    from types import TracebackType

    from iloveapi.typing import T_ImageTools, T_PdfTools
    from iloveapi.utils import cast_omit_self


class ILoveApi:
    def __init__(self, *, public_key: str, secret_key: str) -> None:
        self._public_key = public_key
        self._secret_key = secret_key
        self._sync_client: ContextVar[httpx.Client | None] = ContextVar(
            "sync_client", default=None
        )
        self._async_client: ContextVar[httpx.AsyncClient | None] = ContextVar(
            "async_client", default=None
        )
        self._rest = Rest(self)

    @property
    def public_key(self) -> str:
        # Set the key is unnecessary and will cause context conflict
        return self._public_key

    @property
    def secret_key(self) -> str:
        return self._secret_key

    @property
    def rest(self) -> Rest:
        return self._rest

    def create_task(self, tool: T_PdfTools | T_ImageTools) -> Task:
        return Task.create(self, tool)

    async def create_task_async(self, tool: T_PdfTools | T_ImageTools) -> Task:
        return await Task.create_async(self, tool)

    # sync context
    def __enter__(self) -> Self:
        if self._sync_client.get() is not None:
            raise RuntimeError("Cannot enter sync context twice")
        self._sync_client.set(self._create_sync_client())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        cast(httpx.Client, self._sync_client.get()).close()
        self._sync_client.set(None)

    async def __aenter__(self) -> Self:
        client = self._async_client.get()
        if client is not None:
            raise RuntimeError("Cannot enter context twice")
        self._async_client.set(self._create_async_client())
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await cast(httpx.AsyncClient, self._async_client.get()).aclose()
        self._async_client.set(None)

    def _create_sync_client(self) -> httpx.Client:
        return httpx.Client(
            auth=TokenAuth(self._public_key, self._secret_key),
        )

    def _create_async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            auth=TokenAuth(self._public_key, self._secret_key),
        )

    # get or create sync client
    @contextmanager
    def get_sync_client(self) -> Generator[httpx.Client, None, None]:
        if client := self._sync_client.get():
            yield client
        else:
            client = self._create_sync_client()
            try:
                yield client
            finally:
                client.close()

    # get or create async client
    @asynccontextmanager
    async def get_async_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        if client := self._async_client.get():
            yield client
        else:
            client = self._create_async_client()
            try:
                yield client
            finally:
                await client.aclose()

    # # sync request
    if TYPE_CHECKING:
        request = staticmethod(httpx.request)
    else:

        def request(
            self, method: str, url: httpx.URL | str, **kwargs: Any
        ) -> httpx.Response:
            with self.get_sync_client() as client:
                return client.request(method, url, **kwargs)

    if TYPE_CHECKING:
        request_async = staticmethod(cast_omit_self(httpx.AsyncClient.request))
    else:

        async def request_async(
            self, method: str, url: httpx.URL | str, **kwargs: Any
        ) -> httpx.Response:
            async with self.get_async_client() as client:
                return await client.request(method, url, **kwargs)
