from __future__ import annotations

from io import BytesIO
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

    def _resolve_filename(
        self, file: str | Path | bytes | BytesIO, filename: str | None = None
    ) -> str:
        # No filename or file extension will cause 400 Bad Request
        if isinstance(file, (bytes, BytesIO)):
            if filename is None:
                raise ValueError("filename must be provided for bytes/BytesIO")
        elif isinstance(file, (str, Path)):
            if filename is None:
                filename = Path(file).name
        else:
            raise TypeError("file must be str, Path, bytes or BytesIO")
        return filename

    def add_file(
        self, file: str | Path | bytes | BytesIO, filename: str | None = None
    ) -> str:
        """Add a file to the task.

        Not recommended. Use `process_files` instead.

        Args:
            file: The file to add.
            filename: The filename to use. None to infer from the file path.

        Returns:
            The server filename of the uploaded file.

        """
        filename = self._resolve_filename(file, filename)
        upload_response = self.client.rest.upload(
            self._server, self._task, file, filename=filename
        )
        upload_response.raise_for_status()
        return self._add_file(upload_response, filename)

    async def add_file_async(
        self, file: str | Path | bytes | BytesIO, filename: str | None = None
    ) -> str:
        """Add a file to the task.

        Not recommended. Use `process_files` instead.

        Args:
            file: The file to add.
            filename: The filename to use. None to infer from the file path.

        Returns:
            The server filename of the uploaded file.

        """
        filename = self._resolve_filename(file, filename)
        upload_response = await self.client.rest.upload_async(
            self._server, self._task, file, filename=filename
        )
        upload_response.raise_for_status()
        return self._add_file(upload_response, filename)

    def add_file_by_url(self, url: str, filename: str | None = None) -> str:
        """Add a file to the task by URL.

        Not recommended. Use `process_files` instead.

        Args:
            url: The URL of the file to add.
            filename: The filename to use. None to infer from the URL.

        Returns:
            The server filename of the uploaded file.

        """
        if filename is None:
            # Use the final path component of the URL as the filename
            # Not a best practice, or get from Content-Disposition header
            filename = get_filename_from_url(url)
        upload_response = self.client.rest.upload_url(self._server, self._task, url)
        upload_response.raise_for_status()
        return self._add_file(upload_response, filename)

    async def add_file_by_url_async(self, url: str, filename: str | None = None) -> str:
        """Add a file to the task by URL.

        Not recommended. Use `process_files` instead.

        Args:
            url: The URL of the file to add.
            filename: The filename to use. None to infer from the URL.

        Returns:
            The server filename of the uploaded file.

        """
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
                file = cast("Any", file)
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
        """Process the uploaded files.

        Not recommended. Use `process_files` instead.

        Args:
            files: List of server files to process. None to process all uploaded files.
            **kwargs: Additional parameters to pass to the API.

        """
        proc_files = self._get_process_files(files)
        process_response = self.client.rest.process(
            self._server, self._task, self._tool, proc_files, **kwargs
        )
        process_response.raise_for_status()

    async def process_async(
        self, files: list[_File] | None = None, **kwargs: Any
    ) -> None:
        """Process the uploaded files.

        Not recommended. Use `process_files` instead.

        Args:
            files: List of server files to process. None to process all uploaded files.
            **kwargs: Additional parameters to pass to the API.

        """
        proc_files = self._get_process_files(files)
        process_response = await self.client.rest.process_async(
            self._server, self._task, self._tool, proc_files, **kwargs
        )
        process_response.raise_for_status()

    def _resolve_process_files_file(
        self, file: str | Path | tuple[str, str | Path | bytes | BytesIO] | _UploadFile
    ) -> tuple[str, str | Path | bytes | BytesIO]:
        if isinstance(file, tuple):
            return file
        if isinstance(file, (str, Path)):
            return Path(file).name, file
        if isinstance(file, dict):
            file_ = file["file"]
            filename = file.get("filename")
            if filename is not None:
                return filename, file_
            if isinstance(file_, (str, Path)):
                return Path(file_).name, file_
            raise ValueError("filename must be provided for bytes/BytesIO")
        raise TypeError("file must be str, Path or tuple of filename and file")

    class _UploadFile(TypedDict):
        file: str | Path | bytes | BytesIO
        filename: NotRequired[str]
        rotate: NotRequired[int]
        password: NotRequired[str]

    def _merge_process_file_parameter(
        self, file: Rest._File, upload_file: _UploadFile
    ) -> Rest._File:
        if "rotate" in upload_file:
            file["rotate"] = upload_file["rotate"]
        if "password" in upload_file:
            file["password"] = upload_file["password"]
        return file

    def process_files(
        self,
        *files: str | Path | tuple[str, str | Path | bytes | BytesIO] | _UploadFile,
        **kwargs: Any,
    ) -> None:
        """Upload and process the given files.

        Args:
            files: List of files to process.
                str or Path: File path.
                tuple[str, str | Path | bytes | BytesIO]: Filename and file path or content.
            **kwargs: Additional parameters to pass to the API.

        """
        proc_files: list[Rest._File] = []
        for upload_file in files:
            filename, file = self._resolve_process_files_file(upload_file)
            upload_response = self.client.rest.upload(
                self._server, self._task, file, filename=filename
            )
            upload_response.raise_for_status()
            data = upload_response.json()
            proc_file: Rest._File = {
                "server_filename": data["server_filename"],
                "filename": filename,
            }
            if isinstance(upload_file, dict):
                self._merge_process_file_parameter(proc_file, upload_file)
            proc_files.append(proc_file)
        process_response = self.client.rest.process(
            self._server, self._task, self._tool, proc_files, **kwargs
        )
        process_response.raise_for_status()

    async def process_files_async(
        self,
        *files: str | Path | tuple[str, str | Path | bytes | BytesIO] | _UploadFile,
        **kwargs: Any,
    ) -> None:
        """Upload and process the given files.

        Args:
            files: List of files to process.
                str or Path: File path.
                tuple[str, str | Path | bytes | BytesIO]: Filename and file path or content.
            **kwargs: Additional parameters to pass to the API.

        """
        proc_files: list[Rest._File] = []
        for upload_file in files:
            filename, file = self._resolve_process_files_file(upload_file)
            upload_response = await self.client.rest.upload_async(
                self._server, self._task, file, filename=filename
            )
            upload_response.raise_for_status()
            data = upload_response.json()
            proc_file: Rest._File = {
                "server_filename": data["server_filename"],
                "filename": filename,
            }
            if isinstance(upload_file, dict):
                self._merge_process_file_parameter(proc_file, upload_file)
            proc_files.append(proc_file)
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
