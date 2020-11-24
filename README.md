Giftless Client
===============
A Git LFS client library implemented in Python, compatible with the [
Giftless Git LFS server](https://github.com/datopian/giftless). 

`giftless-client` is tested on Python 2.7 and 3.6+. 

Installation
------------
You can install this library directly from pypi:

```shell script
(venv) $ pip install giftless-client
```

API
---
This module exposes one main class: `LfsClient`. Typically, you only need to use this class to perform most 
Git LFS operations. 

### `LfsClient` class

#### Instantiating a Client
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

#### Downloading a File from LFS storage 

TBD

#### Uploading a File to LFS storage

TBD 

#### Sending an LFS `batch` API request

TBD

Usage in Command Line
---------------------
While the main use for `giftless-client` is as a client library for other projects, this module does include some 
command line functionality.

Run the following command to get more information:

```shell script
(venv) $ giftless-client --help
```

License
-------
Giftless Client is free software distributed under the terms of the MIT license. See [LICENSE](LICENSE) for details.
 
Giftless Client is (c) 2020 Datopian / Viderum Inc.
