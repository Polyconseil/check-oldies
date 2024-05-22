"""A mocker for ``urllib.request.urlopen``."""

import collections
import dataclasses
import json as jsonlib
import typing
import unittest.mock
import urllib.parse
import urllib.request

import pytest


@pytest.fixture(name="requests_mocker")
def get_mock():
    """Return an instance of ``Mock`` to be used as a fixture.

    Example::

        with get_mock() as mock:
            mock.register("GET", "https://example.com", content="OK")
            # call code that would make an HTTP request
    """
    m = Mock()
    with unittest.mock.patch("urllib.request.urlopen", m.urlopen):
        yield m


@dataclasses.dataclass
class Request:
    url: str
    headers: typing.Dict[str, str]
    data: bytes
    params: dict


@dataclasses.dataclass
class Response:
    content: bytes
    status: int

    def read(self):
        return self.content


@dataclasses.dataclass
class Call:
    request: Request
    response: Response


class Mock():
    """Intercept HTTP requests and mock their responses.

    An instance of ``Mock`` can be configured via its two methods:

    - ``get(url: str, json: object, status=200)`` allows you to mock
      the response of a ``GET`` request to particular URL.

    - ``register(method: str, url: str, content: bytes, status=200)``
       is a more generic method.
    """
    def __init__(self):
        self.mocks = collections.defaultdict(dict)
        self.calls = []

    def register(self, method: str, url: str, content: bytes, status: int = 200):
        method = method.lower()
        self.mocks[url][method] = Response(content=content, status=status)

    def get(self, url: str, json: object, status: int = 200):
        content = jsonlib.dumps(json)
        self.register("get", url, content=content.encode("utf-8"), status=status)

    def urlopen(self, request: urllib.request.Request, **kwargs):
        method = request.get_method().lower()
        url = _strip_query_string(request.full_url)
        response = self.mocks.get(url, {}).get(method)
        if not response:
            raise ValueError(f"No mock for method={method} and url={url}")
        call = Call(
            request=Request(
                url=url,
                headers=dict(request.headers),  # MutableMapping -> dict
                data=request.data or b'',  # type: ignore [arg-type]
                params=_extract_params(request),
            ),
            response=response,
        )
        self.calls.append(call)
        return response


def _strip_query_string(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return parsed._replace(query="").geturl()


def _extract_params(request: urllib.request.Request) -> dict:
    query = urllib.parse.urlparse(request.full_url).query
    if not query:
        return {}
    params = urllib.parse.parse_qs(query)
    for key, values in params.items():
        if len(values) == 1:
            params[key] = values[0]  # type: ignore [assignment]
    return params
