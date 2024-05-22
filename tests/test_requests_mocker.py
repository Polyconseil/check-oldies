import urllib.request

from . import requests_mocker


def test_extract_params():
    url = "https://example.com/?single=1&multiple=2&multiple=3&empty="
    request = urllib.request.Request(url)
    params = requests_mocker._extract_params(request)
    assert params == {"single": "1", "multiple": ["2", "3"]}


def test_strip_query_string():
    url = "https://example.com/path?foo=1"
    stripped = requests_mocker._strip_query_string(url)
    assert stripped == "https://example.com/path"
