from __future__ import division

import base64
import hashlib
import logging
from typing import Any, BinaryIO, Dict, Optional, Union

import requests

from . import types

_log = logging.getLogger(__name__)


class BasicTransferAdapter(object):

    def upload(self, file_obj, upload_spec):
        # type: (BinaryIO, types.UploadObjectAttributes) -> None
        try:
            ul_action = upload_spec['actions']['upload']
        except KeyError:  # Object is already on the server
            return

        reply = requests.put(ul_action['href'], headers=ul_action.get('header', {}), data=file_obj)
        if reply.status_code // 100 != 2:
            raise RuntimeError("Unexpected reply from server for upload: {} {}".format(reply.status_code, reply.text))

        vfy_action = upload_spec['actions'].get('verify')
        if vfy_action:
            self._verify_object(vfy_action, upload_spec['oid'], upload_spec['size'])

    def download(self, file_obj, download_spec):
        # type: (BinaryIO, types.DownloadObjectAttributes) -> None
        """Download an object from LFS
        """
        dl_action = download_spec['actions']['download']
        with requests.get(dl_action['href'], headers=dl_action.get('header', {}), stream=True) as response:
            for chunk in response.iter_content(1024 * 16):
                file_obj.write(chunk)

    @staticmethod
    def _verify_object(verify_action, oid, size):
        # type: (types.BasicActionAttributes, str, int) -> None
        _log.info("Sending verify action to %s", verify_action['href'])
        response = requests.post(verify_action['href'], headers=verify_action.get('header', {}),
                                 json={"oid": oid, "size": size})
        if response.status_code // 100 != 2:
            raise RuntimeError("verify failed with error status code: {}: {}".format(
                response.status_code, response.text))


class MultipartTransferAdapter(BasicTransferAdapter):

    def upload(self, file_obj, upload_spec):
        # type: (BinaryIO, types.MultipartUploadObjectAttributes) -> None
        """Do a multipart upload
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
            self._verify_object(verify_action, upload_spec['oid'], upload_spec['size'])

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
