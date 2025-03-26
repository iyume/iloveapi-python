from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    import httpx

    from iloveapi.iloveapi import ILoveApi
    from iloveapi.typing import T_ImageTools, T_PdfTools


class Rest:
    def __init__(self, client: ILoveApi) -> None:
        self.client = client

    def start(self, tool: T_PdfTools | T_ImageTools) -> httpx.Response:
        url = f"https://api.ilovepdf.com/v1/start/{tool}"
        return self.client.request("GET", url)

    async def start_async(self, tool: T_PdfTools | T_ImageTools) -> httpx.Response:
        url = f"https://api.ilovepdf.com/v1/start/{tool}"
        return await self.client.request_async("GET", url)

    def upload(
        self,
        server: str,
        task: str,
        file: str | Path | bytes | BytesIO,
        filename: str | None = None,
        chunk: int | None = None,
        chunks: int | None = None,
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload"
        if chunk or chunks:
            raise NotImplementedError("Chunked uploads are not supported")
        if isinstance(file, (bytes, BytesIO)) and not filename:
            raise ValueError("Filename is required for bytes or BytesIO file")
        if isinstance(file, (Path, str)):
            filebuf = open(file, "rb")
        else:
            filebuf = (filename, file)
        return self.client.request(
            "POST",
            url,
            data={"task": task},
            files={"file": filebuf},
        )

    async def upload_async(
        self,
        server: str,
        task: str,
        file: str | Path | bytes | BytesIO,
        filename: str | None = None,
        chunk: int | None = None,
        chunks: int | None = None,
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload"
        if chunk or chunks:
            raise NotImplementedError("Chunked uploads are not supported")
        if isinstance(file, (bytes, BytesIO)) and not filename:
            raise ValueError("Filename is required for bytes or BytesIO file")
        if isinstance(file, (Path, str)):
            filebuf = open(file, "rb")
        else:
            filebuf = (filename, file)
        return await self.client.request_async(
            "POST",
            url,
            data={"task": task},
            files={"file": filebuf},
        )

    def upload_url(
        self, server: str, task: str, cloud_file: str | None = None
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload"
        return self.client.request(
            "POST", url, data={"task": task, "cloud_file": cloud_file}
        )

    async def upload_url_async(
        self, server: str, task: str, cloud_file: str | None = None
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload"
        return await self.client.request_async(
            "POST", url, data={"task": task, "cloud_file": cloud_file}
        )

    def delete_file(
        self, server: str, task: str, server_filename: str
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload/{task}/{server_filename}"
        return self.client.request("DELETE", url)

    async def delete_file_async(
        self, server: str, task: str, server_filename: str
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload/{task}/{server_filename}"
        return await self.client.request_async("DELETE", url)

    class _File(TypedDict):
        server_filename: str
        filename: str
        rotate: NotRequired[int]
        password: NotRequired[str]

    def process(
        self,
        server: str,
        task: str,
        tool: T_PdfTools | T_ImageTools,
        files: list[_File],
        **kwargs: Any,
    ) -> httpx.Response:
        url = f"https://{server}/v1/process"
        return self.client.request(
            "POST", url, json={"task": task, "tool": tool, "files": files} | kwargs
        )

    async def process_async(
        self,
        server: str,
        task: str,
        tool: T_PdfTools | T_ImageTools,
        files: list[_File],
        **kwargs: Any,
    ) -> httpx.Response:
        url = f"https://{server}/v1/process"
        return await self.client.request_async(
            "POST", url, json={"task": task, "tool": tool, "files": files} | kwargs
        )

    def download(self, server: str, task: str) -> httpx.Response:
        url = f"https://{server}/v1/download/{task}"
        return self.client.request("GET", url)

    async def download_async(self, server: str, task: str) -> httpx.Response:
        url = f"https://{server}/v1/download/{task}"
        return await self.client.request_async("GET", url)

    def tasks(self, **kwargs: Any) -> httpx.Response:
        url = "https://api.ilovepdf.com/v1/task"
        return self.client.request(
            "POST", url, json={"secret_key": self.client.secret_key} | kwargs
        )

    async def tasks_async(self, **kwargs: Any) -> httpx.Response:
        url = "https://api.ilovepdf.com/v1/task"
        return await self.client.request_async(
            "POST", url, json={"secret_key": self.client.secret_key} | kwargs
        )

    def delete_task(self, server: str, task: str) -> httpx.Response:
        url = f"https://{server}/v1/task/{task}"
        return self.client.request("DELETE", url)

    async def delete_task_async(self, server: str, task: str) -> httpx.Response:
        url = f"https://{server}/v1/task/{task}"
        return await self.client.request_async("DELETE", url)

    def connect_task(self, server: str, task: str, tool: str) -> httpx.Response:
        url = f"https://{server}/v1/task/next"
        return self.client.request("POST", url, json={"task": task, "tool": tool})

    async def connect_task_async(
        self, server: str, task: str, tool: str
    ) -> httpx.Response:
        url = f"https://{server}/v1/task/next"
        return await self.client.request_async(
            "POST", url, json={"task": task, "tool": tool}
        )
