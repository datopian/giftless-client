"""Some useful type definitions for Git LFS API and transfer protocols
"""
import sys
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


ObjectAttributes = TypedDict('ObjectAttributes', {
    'oid': str,
    'size': int,
})

BasicActionAttributes = TypedDict('BasicActionAttributes', {
    'href': str,
    'header': Optional[Dict[str, str]],
    'expires_in': int
})

BasicUploadActions = TypedDict('BasicUploadActions', {
    'upload': BasicActionAttributes,
    'verify': BasicActionAttributes,
}, total=False)

BasicDownloadActions = TypedDict('BasicDownloadActions', {
    'download': BasicActionAttributes,
}, total=False)

UploadObjectAttributes = TypedDict('UploadObjectAttributes', {
    'actions': BasicUploadActions,
    'oid': str,
    'size': int,
    'authenticated': Optional[bool],
}, total=False)

DownloadObjectAttributes = TypedDict('DownloadObjectAttributes', {
    'actions': BasicDownloadActions,
    'oid': str,
    'size': int,
    'authenticated': Optional[bool],
}, total=False)

MultipartUploadActions = TypedDict('MultipartUploadActions', {
    'init': Dict[str, Any],
    'commit': Dict[str, Any],
    'parts': List[Dict[str, Any]],
    'abort': Dict[str, Any],
    'verify': Dict[str, Any],
}, total=False)

MultipartUploadObjectAttributes = TypedDict('MultipartUploadObjectAttributes', {
    'actions': MultipartUploadActions,
    'oid': str,
    'size': int,
    'authenticated': Optional[bool],
}, total=False)
