"""A simple Git LFS client
"""
import base64
import hashlib
import logging
import os
from typing import Any, BinaryIO, Dict, Optional, Union

import requests
from six.moves import urllib

from . import types

FILE_READ_BUFFER_SIZE = 4 * 1024 * 1000  # 4mb, why not

_log = logging.getLogger(__name__)


class LfsClient:

    def __init__(self, lfs_server_url, auth_token=None):
        # type: (str, Optional[str]) -> LfsClient
        self._url = lfs_server_url.rstrip('/')
        self._auth_token = auth_token

    def upload(self, file_obj, organization, repo):
        # type: (BinaryIO, str, str) -> None
        """Upload a file to LFS storage
        """
        object_attrs = self._get_object_attrs(file_obj)
        payload = {"transfers": ["multipart-basic", "basic"],
                   "operation": "upload",
                   "objects": [object_attrs]}
        batch_reply = requests.post(self._url_for(organization, repo, 'objects', 'batch'), json=payload)
        if batch_reply.status_code != 200:
            raise RuntimeError("Unexpected reply from LFS server: {}".format(batch_reply))

        response = batch_reply.json()
        _log.debug("Got reply for batch request: %s", response)

        if response['transfer'] == 'basic':
            return self._upload_basic(file_obj, response['objects'][0])
        elif response['transfer'] == 'multipart-basic':
            return self._upload_multipart(file_obj, response['objects'][0])

    def _url_for(self, *segments, **params):
        # type: (str, str) -> str
        path = os.path.join(*segments)
        url = '{url}/{path}'.format(url=self._url, path=path)
        if params:
            url = '{url}?{params}'.format(url=url, params=urllib.parse.urlencode(params))
        return url

    def _upload_basic(self, file_obj, upload_spec):
        # type: (BinaryIO, types.UploadObjectAttributes) -> None
        """Do a basic upload
        TODO: refactor this into a separate class
        """
        raise NotImplementedError("Basic uploads are not implemented yet")

    def _upload_multipart(self, file_obj, upload_spec):
        # type: (BinaryIO, types.MultipartUploadObjectAttributes) -> None
        """Do a multipart upload
        TODO: refactor this into a separate class
        """
        actions = upload_spec.get('actions')
        if not actions:
            _log.info("No actions, file already exists")
            return

        init_action = actions.get('init')
        if init_action:
            _log.info("Sending multipart init action to %s", init_action['href'])
            response = self._send_request(init_action['href'],
                                          method=init_action.get('method', 'POST'),
                                          headers=init_action.get('header', {}),
                                          body=init_action.get('body'))
            if response.status_code // 100 != 2:
                raise RuntimeError("init failed with error status code: {}".format(response.status_code))

        for p, part in enumerate(actions.get('parts', [])):
            _log.info("Uploading part %d/%d", p + 1, len(actions['parts']))
            self._send_part_request(file_obj, **part)

        commit_action = actions.get('commit')
        if commit_action:
            _log.info("Sending multipart commit action to %s", commit_action['href'])
            response = self._send_request(commit_action['href'],
                                          method=commit_action.get('method', 'POST'),
                                          headers=commit_action.get('header', {}),
                                          body=commit_action.get('body'))
            if response.status_code // 100 != 2:
                raise RuntimeError("commit failed with error status code: {}: {}".format(
                    response.status_code, response.text))

        verify_action = actions.get('verify')
        if verify_action:
            _log.info("Sending verify action to %s", verify_action['href'])
            response = requests.post(verify_action['href'], headers=verify_action.get('header', {}),
                                     json={"oid": upload_spec['oid'], "size": upload_spec['size']})
            if response.status_code // 100 != 2:
                raise RuntimeError("verify failed with error status code: {}: {}".format(
                    response.status_code, response.text))

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

    def _send_part_request(self, file_obj, href, method='PUT', pos=0, size=None, want_digest=None, header=None, **_):
        # type: (BinaryIO, str, str, int, Optional[int], Optional[str], Optional[Dict[str, Any]], Any) -> None
        """Upload a part
        """
        file_obj.seek(pos)
        if size:
            data = file_obj.read(size)
        else:
            data = file_obj.read()

        if header is None:
            header = {}

        if want_digest:
            digest_headers = calculate_digest_header(data, want_digest)
            header.update(digest_headers)

        reply = self._send_request(href, method=method, headers=header, body=data)
        if reply.status_code // 100 != 2:
            raise RuntimeError("Unexpected reply from server for part: {} {}".format(reply.status_code, reply.text))

    @staticmethod
    def _send_request(url, method, headers, body=None):
        # type: (str, str, Dict[str, str], Union[bytes, str, None]) -> requests.Response
        """Send an arbitrary HTTP request
        """
        reply = requests.session().request(method=method, url=url, headers=headers, data=body)
        return reply


def calculate_digest_header(data, want_digest):
    # type: (bytes, str) -> Dict[str, str]
    """TODO: Properly implement this
    """
    if want_digest == 'contentMD5':
        digest = base64.b64encode(hashlib.md5(data).digest()).decode('ascii')  # type: str
        return {'Content-MD5': digest}
    else:
        raise RuntimeError("Don't know how to handle want_digest value: {}".format(want_digest))
