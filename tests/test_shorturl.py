import unittest
from typing import Any

import requests
from unittest.mock import MagicMock

from icakad.shorturl import DEFAULT_TIMEOUT, ShortURLClient, ShortURLError, _extract_items


class DummyResponse:
    def __init__(self, *, status: int = 200, payload: Any = None, text: str = "", reason: str = "ERR") -> None:
        self.status_code = status
        self._payload = payload
        self.text = text
        self.reason = reason

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError("boom")

    def json(self) -> Any:
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class ShortURLHelpersTests(unittest.TestCase):
    def test_extract_items_supports_dicts_and_lists(self) -> None:
        payload = {
            "items": [
                {"slug": "one"},
                {"slug": "two"},
                "skip",
            ]
        }
        self.assertEqual(_extract_items(payload), [{"slug": "one"}, {"slug": "two"}])
        self.assertEqual(_extract_items([{"slug": "three"}, "x"]), [{"slug": "three"}])

    def test_headers_include_authorization_when_token_present(self) -> None:
        client = ShortURLClient(base_url="https://linkove.icu", token="abc123")
        headers = client._headers()
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer abc123")

    def test_request_wraps_http_errors(self) -> None:
        session = MagicMock(spec=requests.Session)
        session.post.return_value = DummyResponse(status=500, text="boom")
        client = ShortURLClient(base_url="https://example.com", session=session)
        with self.assertRaises(ShortURLError) as ctx:
            client.add_link("slug", "https://target")
        self.assertIn("500", str(ctx.exception))

    def test_list_links_supports_alternate_field_names(self) -> None:
        session = MagicMock(spec=requests.Session)
        session.get.return_value = DummyResponse(
            payload={
                "list": [
                    {"key": "one", "value": "https://one"},
                    {"name": "two", "url": "https://two"},
                    {"slug": 123, "url": "skip"},
                ]
            }
        )
        client = ShortURLClient(base_url="https://example.com", session=session, token="token")
        links = client.list_links()
        self.assertEqual(links, {"one": "https://one", "two": "https://two"})

    def test_list_links_raises_on_invalid_json(self) -> None:
        session = MagicMock(spec=requests.Session)
        session.get.return_value = DummyResponse(payload=ValueError("bad json"))
        client = ShortURLClient(base_url="https://example.com", session=session)
        with self.assertRaises(ShortURLError):
            client.list_links()

    def test_json_helper_rejects_non_dict_payloads(self) -> None:
        client = ShortURLClient(base_url="https://example.com")
        response = DummyResponse(payload=["unexpected"])
        with self.assertRaises(ShortURLError):
            client._json(response)

    def test_default_timeout_is_exposed(self) -> None:
        client = ShortURLClient(base_url="https://example.com")
        self.assertEqual(client.timeout, DEFAULT_TIMEOUT)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
