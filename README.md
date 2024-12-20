# iloveapi-python

Python api client made for ILoveIMG & ILovePDF based on ILoveAPI (https://www.iloveapi.com/docs/api-reference).

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
task.add_file("p1.png")
task.process()
task.download("output.png")
```

Directly call REST API:

```python
response = client.rest.start("compressimage")  # getting httpx response
response = await client.rest.start_async("compressimage")  # async
```

Async support:

```python
task = await client.create_task_async("compressimage")
await task.add_file_async("p1.png")
await task.process_async()
await task.download_async("output.png")
```

## TODO

- [ ] Typed parameter for all processing tools
- [ ] Command-line interface

## Why not pydantic?

Image / PDF processing tools usually focus on results rather than JSON data, as data type validation is not important to the user.
