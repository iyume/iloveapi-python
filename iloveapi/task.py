from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast, overload

from typing_extensions import NotRequired, Self

from iloveapi.utils import get_filename_from_url, to_dict

if TYPE_CHECKING:
    import httpx

    from iloveapi.iloveapi import ILoveApi
    from iloveapi.rest import Rest
    from iloveapi.typing import T_ImageTools, T_PdfTools


class _UploadedFile(TypedDict):
    server_filename: str
    filename: str  # final path component


class Task:
    def __init__(
        self, client: ILoveApi, server: str, task: str, tool: T_PdfTools | T_ImageTools
    ) -> None:
        self.client = client
        self._server = server
        self._task = task
        self._tool: T_PdfTools | T_ImageTools = tool
        self._uploaded_files: list[_UploadedFile] = []

    @classmethod
    def create(cls, client: ILoveApi, tool: T_PdfTools | T_ImageTools) -> Self:
        task_response = client.rest.start(tool)
        task_response.raise_for_status()
        task_json = task_response.json()
        return cls(client, task_json["server"], task_json["task"], tool)

    @classmethod
    async def create_async(
        cls, client: ILoveApi, tool: T_PdfTools | T_ImageTools
    ) -> Self:
        task_response = await client.rest.start_async(tool)
        task_response.raise_for_status()
        data = task_response.json()
        return cls(client, data["server"], data["task"], tool)

    def add_file(self, file: str | Path) -> str:
        if not isinstance(file, Path):
            file = Path(file)
        upload_response = self.client.rest.upload(self._server, self._task, file)
        upload_response.raise_for_status()
        return self._add_file(upload_response, file.name)

    async def add_file_async(self, file: str | Path) -> str:
        if not isinstance(file, Path):
            file = Path(file)
        upload_response = await self.client.rest.upload_async(
            self._server, self._task, file
        )
        upload_response.raise_for_status()
        return self._add_file(upload_response, file.name)

    def add_file_by_url(self, url: str, filename: str | None = None) -> str:
        if filename is None:
            # Use the final path component of the URL as the filename
            # Not a best practice, or get from Content-Disposition header
            filename = get_filename_from_url(url)
        upload_response = self.client.rest.upload_url(self._server, self._task, url)
        upload_response.raise_for_status()
        return self._add_file(upload_response, filename)

    async def add_file_by_url_async(self, url: str, filename: str | None = None) -> str:
        if filename is None:
            filename = get_filename_from_url(url)
        upload_response = await self.client.rest.upload_url_async(
            self._server, self._task, url
        )
        upload_response.raise_for_status()
        return self._add_file(upload_response, filename)

    def _add_file(self, response: httpx.Response, filename: str) -> str:
        data = response.json()
        server_filename = data["server_filename"]
        self._uploaded_files.append(
            {"server_filename": server_filename, "filename": filename}
        )
        return server_filename

    class _File(TypedDict):
        server_filename: str
        # Download filename. None to use the original filename
        filename: NotRequired[str]
        rotate: NotRequired[int]
        password: NotRequired[str]

    def _get_process_files(self, files: list[_File] | None) -> list[Rest._File]:
        proc_files: list[Rest._File]
        # Duplicate filename are processed as "{filename}-copy-0"
        if files is None:
            proc_files = [
                {
                    "server_filename": file["server_filename"],
                    "filename": file["filename"],
                }
                for file in self._uploaded_files
            ]
        elif len(files) == 0:
            raise ValueError("files must not be empty")
        else:
            uploaded_files = to_dict(self._uploaded_files, "server_filename")
            proc_files = []
            for file in files:
                file = cast(Any, file)
                server_filename = file.pop("server_filename")
                filename = file.pop("filename")
                uploaded_file = uploaded_files.get(server_filename)
                if uploaded_file is None:
                    raise ValueError(f"File {server_filename} not uploaded")
                proc_files.append(
                    {
                        "server_filename": server_filename,
                        "filename": filename or uploaded_file["filename"],
                        **file,
                    }
                )
        return proc_files

    def process(self, files: list[_File] | None = None, **kwargs: Any) -> None:
        proc_files = self._get_process_files(files)
        process_response = self.client.rest.process(
            self._server, self._task, self._tool, proc_files, **kwargs
        )
        process_response.raise_for_status()

    async def process_async(
        self, files: list[_File] | None = None, **kwargs: Any
    ) -> None:
        proc_files = self._get_process_files(files)
        process_response = await self.client.rest.process_async(
            self._server, self._task, self._tool, proc_files, **kwargs
        )
        process_response.raise_for_status()

    @overload
    def download(self, output_file: None = None) -> bytes: ...

    @overload
    def download(self, output_file: str | Path) -> None: ...

    def download(self, output_file: str | Path | None = None) -> bytes | None:
        download_response = self.client.rest.download(self._server, self._task)
        download_response.raise_for_status()
        return self._download(download_response, output_file)

    @overload
    async def download_async(self, output_file: None = None) -> bytes: ...

    @overload
    async def download_async(self, output_file: str | Path) -> None: ...

    async def download_async(
        self, output_file: str | Path | None = None
    ) -> bytes | None:
        download_response = await self.client.rest.download_async(
            self._server, self._task
        )
        download_response.raise_for_status()
        return self._download(download_response, output_file)

    def _download(
        self, response: httpx.Response, output_file: str | Path | None
    ) -> bytes | None:
        if output_file is None:
            return response.content
        if not isinstance(output_file, Path):
            output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(response.content)
        return None
