"""some basic tests for the client module
"""
import pytest

from giftless_client import client


@pytest.mark.parametrize('want_digest,expected', [
    ('contentMD5', {'Content-MD5': 'Ucl1jPqv8moo9k37HPoBnA=='})
])
def test_calculate_want_digest(want_digest, expected):
    """Test that want_digest is handled properly
    """
    data = b'Why not Zoidberg?'
    assert expected == client.calculate_digest_header(data, want_digest)
