from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    import httpx

    from iloveapi.iloveapi import ILoveApi

T_PdfTools = Literal[
    "compress",
    "extract",
    "htmlpdf",
    "imagepdf",
    "merge",
    "officepdf",
    "pagenumber",
    "pdfa",
    "pdfjpg",
    "pdfocr",
    "protect",
    "repair",
    "rotate",
    "split",
    "unlock",
    "validatepdfa",
    "watermark",
]
T_ImageTools = Literal[
    "compressimage",
    "cropimage",
    "convertimage",
    "removebackgroundimage",
    "repairimage",
    "resizeimage",
    "rotateimage",
    "upscaleimage",
    "watermarkimage",
]


class Rest:
    def __init__(self, client: ILoveApi) -> None:
        self.client = client

    def start(self, tool: T_PdfTools | T_ImageTools) -> httpx.Response:
        url = f"https://api.ilovepdf.com/v1/start/{tool}"
        with self.client.get_sync_client() as client:
            return client.get(url)

    def upload(
        self,
        server: str,
        task: str,
        file: str | Path,
        chunk: int | None = None,
        chunks: int | None = None,
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload"
        if chunk or chunks:
            raise NotImplementedError("Chunked uploads are not supported")
        file = Path(file)
        return self.client.request(
            "POST",
            url,
            data={"task": task},
            files={"file": (file.name, file.open("rb"))},
        )

    def upload_url(
        self, server: str, task: str, cloud_file: str | None = None
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload"
        return self.client.request(
            "POST", url, data={"task": task, "cloud_file": cloud_file}
        )

    def delete_file(
        self, server: str, task: str, server_filename: str
    ) -> httpx.Response:
        url = f"https://{server}/v1/upload/{task}/{server_filename}"
        return self.client.request("DELETE", url)

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

    def download(self, server: str, task: str) -> httpx.Response:
        url = f"https://{server}/v1/download/{task}"
        return self.client.request("GET", url)

    def tasks(self, **kwargs: Any) -> httpx.Response:
        url = "https://api.ilovepdf.com/v1/task"
        return self.client.request(
            "POST", url, json={"secret_key": self.client.secret_key} | kwargs
        )

    def delete_task(self, server: str, task: str) -> httpx.Response:
        url = f"https://{server}/v1/task/{task}"
        return self.client.request("DELETE", url)

    def connect_task(self, server: str, task: str, tool: str) -> httpx.Response:
        url = f"https://{server}/v1/task/next"
        return self.client.request("POST", url, json={"task": task, "tool": tool})
