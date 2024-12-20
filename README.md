# iloveapi-python

Python api client made for iLoveIMG & iLovePDF based on iLoveAPI (https://www.iloveapi.com/docs/api-reference).

## Features

- Fully typed code
- Asyncio support
- REST API & workflow API encapsulation

## Installation

```shell
pip install iloveapi
```

## Getting Started

Simply compress image:

```python
from iloveapi import ILoveApi

client = ILoveApi(
    public_key="<project_public_******>",
    secret_key="<secret_key_******>",
)
task = client.create_task("compressimage")
task.process_files("p1.png")
task.download("output.png")
```

Multiple images:

```python
task = client.create_task("compressimage")
task.process_files(
    "p1.png",
    ("custom_name.png", "p2.png"),
    ("custom_name.png", b"..PNG..."),
    {
        "file": b"..PNG...",
        "filename": "custom_name.png",
        "rotate": 2,  # add image parameter
        "password": "xxx",  # for PDF
    }
)
task.download("output.zip")  # zip format
```

Async support:

```python
task = await client.create_task_async("compressimage")
await task.process_files_async("p1.png")
await task.download_async("output.png")
```

Directly call REST API:

```python
response = client.rest.start("compressimage")  # getting httpx response
response = await client.rest.start_async("compressimage")  # async
```

## TODO

- [ ] Typed parameter for all processing tools
- [ ] Command-line interface

## Why not pydantic?

Image / PDF processing tools usually focus on results rather than JSON data, as data type validation is not important to the user.
