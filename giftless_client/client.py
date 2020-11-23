"""A simple Git LFS client
"""
import hashlib
import logging
import os
from typing import BinaryIO, Iterable, Optional

import requests
from six.moves import urllib_parse

from . import transfer, types

FILE_READ_BUFFER_SIZE = 4 * 1024 * 1000  # 4mb, why not

_log = logging.getLogger(__name__)


class LfsClient(object):

    TRANSFER_ADAPTERS = {'basic': transfer.BasicTransferAdapter,
                         'multipart-basic': transfer.MultipartTransferAdapter}

    TRANSFER_ADAPTER_PRIORITY = ('multipart-basic', 'basic')

    def __init__(self, lfs_server_url, auth_token=None, transfer_adapters=TRANSFER_ADAPTER_PRIORITY):
        # type: (str, Optional[str], Iterable[str]) -> LfsClient
        self._url = lfs_server_url.rstrip('/')
        self._auth_token = auth_token
        self._transfer_adapters = transfer_adapters

    def upload(self, file_obj, organization, repo):
        # type: (BinaryIO, str, str) -> None
        """Upload a file to LFS storage

        TODO: allow specifying more than one file for a single batch operation
        """
        object_attrs = self._get_object_attrs(file_obj)
        payload = {"transfers": self._transfer_adapters,
                   "operation": "upload",
                   "objects": [object_attrs]}
        batch_reply = requests.post(self._url_for(organization, repo, 'objects', 'batch'), json=payload)
        if batch_reply.status_code != 200:
            raise RuntimeError("Unexpected reply from LFS server: {}".format(batch_reply))

        response = batch_reply.json()
        _log.debug("Got reply for batch request: %s", response)

        try:
            adapter = self.TRANSFER_ADAPTERS[response['transfer']]()
        except KeyError:
            raise ValueError("Unsupported transfer adapter: {}".format(response['transfer']))

        return adapter.upload(file_obj, response['objects'][0])

    def _url_for(self, *segments, **params):
        # type: (str, str) -> str
        path = os.path.join(*segments)
        url = '{url}/{path}'.format(url=self._url, path=path)
        if params:
            url = '{url}?{params}'.format(url=url, params=urllib_parse.urlencode(params))
        return url

    @staticmethod
    def _get_object_attrs(file_obj):
        # type: (BinaryIO) -> types.ObjectAttributes
        digest = hashlib.sha256()
        try:
            while True:
                data = file_obj.read(FILE_READ_BUFFER_SIZE)
                if data:
                    digest.update(data)
                else:
                    break

            size = file_obj.tell()
            oid = digest.hexdigest()
        finally:
            file_obj.seek(0)

        return types.ObjectAttributes(oid=oid, size=size)
