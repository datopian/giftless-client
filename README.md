# Giftless Client

A Git LFS client library implemented in Python, compatible with Git LFS servers in general and specifically [Giftless Git LFS server](https://github.com/datopian/giftless). 

`giftless-client` is tested on Python 2.7 and 3.6+. 

## Installation

You can install this library directly from pypi:

```shell script
(venv) $ pip install giftless-client
```

## API

This module exposes one main class: `LfsClient`. Typically, you only need to use this class to perform most Git LFS operations. The client provides both a wrapper around the low-level LFS API commands e.g. `batch` as well as higher level methods to upload and download files.

### Instantiating a Client

```python
from giftless_client import LfsClient

client = LfsClient(
    lfs_server_url='https://git-lfs.example.com', # Git LFS server URL
    auth_token='somer4nd0mT0ken==',               # Bearer token if required by the server (optional)
    transfer_adapters=['basic']                   # Enabled transfer adapters (optional)
)
```
The `transfer_adapters` parameter is optional, and represents a list of supported transfer adapters by priority
to negotiate with the server; Typically, there is no reason to provide this parameter.

### Downloading a File from LFS storage 

Download a file and save it to file like object.

```python
download(file_obj, object_sha256, object_size, organization, repo, **extras)
```

* `file_obj` is expected to be an file-like object open for writing in binary mode
* `object_sha256`: sha256 of the object you wish to download
* `object_size`: size of the object you wish to download
* `organization`, `repo`: used to generate the prefix for the batch request in form `organization/repo`
* `extras` are added to the batch request attributes dict prefixed with `x-`. This is largely Giftless specific.

Note that the download itself is performed by the selected [Transfer Adapter][transfer].

[transfer]: https://github.com/datopian/giftless-client/blob/master/giftless_client/transfer.py

### Uploading a File to LFS storage

Upload a file to LFS storage

```
upload(file_obj, organization, repo, **extras)
```

* `file_obj`: a readable, seekable file-like object
* Other arguments as per download

Note that the upload itself is performed by the selected [Transfer Adapter][transfer].

[transfer]: https://github.com/datopian/giftless-client/blob/master/giftless_client/transfer.py

### Sending an LFS `batch` API request

Send a [`batch` request][batch] to the LFS server:

`batch(prefix, operation, objects, ref=None, transfers=None)`

* `prefix`: add to LFS server url e.g. if `prefix=abc` and client was created with server url of `https://git-lfs.example.com` then batch request is made by POST to `https://git-lfs.example.com/abc/objects/batch`
* All other arguments: see [batch command][batch] for definitions 

[batch]: https://github.com/git-lfs/git-lfs/blob/master/docs/api/batch.md

Example:

```
client.batch(
  prefix='myorg/myrepo',
  operation='download',
  objects={
      "oid": "12345678",
      "size": 123
    }
)
```

## Usage in Command Line

While the main use for `giftless-client` is as a client library for other projects, this module does include some 
command line functionality.

Run the following command to get more information:

```shell script
(venv) $ giftless-client --help
```

## License

Giftless Client is free software distributed under the terms of the MIT license. See [LICENSE](LICENSE) for details.
 
Giftless Client is (c) 2020 Datopian / Viderum Inc.
