"""Some useful type definitions for Git LFS API and transfer protocols
"""
import sys
from typing import Any, Dict, List

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


ObjectAttributes = TypedDict('ObjectAttributes', {
    'oid': str,
    'size': str,
})

BasicUploadActions = TypedDict('BasicUploadActions', {
    'upload': Dict[str, Any],
    'verify': Dict[str, Any],
}, total=False)

UploadObjectAttributes = TypedDict('UploadObjectAttributes', {
    'actions': BasicUploadActions,
    'oid': str,
    'size': str,
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
    'size': str,
}, total=False)
