from types import SimpleNamespace

import requests

from screenshot_ocr.ocr_client import SiliconFlowOCR


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_request_retries_after_timeout(monkeypatch):
    client = SiliconFlowOCR(api_key="sk-test")
    calls = {"count": 0}

    def fake_post(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.exceptions.Timeout()
        return FakeResponse(payload={"choices": [{"message": {"content": "line-1"}}]})

    monkeypatch.setattr(requests, "post", fake_post)

    result = client._request({"demo": True})

    assert calls["count"] == 2
    assert result["choices"][0]["message"]["content"] == "line-1"


def test_parse_response_deduplicates_lines():
    client = SiliconFlowOCR(api_key="sk-test")
    payload = {
        "choices": [
            {
                "message": {
                    "content": "A\nA\nB B\n"
                }
            }
        ]
    }

    assert client._parse_response(payload) == ["A", "B"]


def test_request_raises_on_non_200(monkeypatch):
    client = SiliconFlowOCR(api_key="sk-test")
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: FakeResponse(status_code=500, text="server error"),
    )

    try:
        client._request({"demo": True})
    except Exception as exc:
        assert "状态码 500" in str(exc)
    else:
        raise AssertionError("Expected _request to raise on non-200 response")
