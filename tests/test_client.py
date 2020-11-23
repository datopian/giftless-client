from giftless_client.client import LfsClient


def _fake_object():
    return {
        "oid": "4ae7c3b6ac0beff671efa8cf57386151c06e58ca53a78d83f36107316cec125f",
        "size": 12
    }


def test_client_batch(requests_mock):
    obj1 = _fake_object()
    requests_mock.post('http://myserver.com/myorg/myrepo/objects/batch', json={
        "transfer": "basic",
        "objects": [{"oid": obj1['oid'],
                     "size": obj1['size'],
                     "actions": {
                        "download": {
                            "href": "https://storage.myserver.com/myorg/myrepo/getthatfile",
                            "header": {"Authorization": "Bearer sometoken"},
                            "expires_at": "2021-11-10T15:29:07Z"
                        }
                    }
        }]
    })
    client = LfsClient('http://myserver.com')
    response = client.batch('myorg/myrepo', 'download', [obj1])
    assert response['transfer'] == 'basic'
