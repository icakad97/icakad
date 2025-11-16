import unittest
from unittest.mock import MagicMock, patch

import requests

from icakad.paste import PasteClient, PasteError


class DummyResponse:
    def __init__(self, *, status: int = 200, payload=None, text: str = "", reason: str = "ERR") -> None:
        self.status_code = status
        self._payload = payload
        self.text = text
        self.reason = reason

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError("boom")

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class PasteClientTests(unittest.TestCase):
    def test_headers_include_accept_authorization_and_content_type(self) -> None:
        client = PasteClient(base_url="https://example.com", token="abc")
        headers = client._headers(content_type="application/json")
        self.assertEqual(headers["Accept"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer abc")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_create_paste_plaintext_branch_sends_raw_body(self) -> None:
        session = MagicMock()
        session.post.return_value = DummyResponse(payload={"ok": True})
        client = PasteClient(base_url="https://example.com", token="tok", session=session)
        result = client.create_paste("hello", paste_id="abc", ttl=30, as_plaintext=True)
        self.assertTrue(result["ok"])
        session.post.assert_called_with(
            "https://example.com/api/paste",
            params={"id": "abc", "ttl": 30},
            data="hello",
            headers={
                "Accept": "application/json",
                "Content-Type": "text/plain; charset=utf-8",
                "Authorization": "Bearer tok",
            },
            timeout=10,
        )

    def test_create_paste_requires_non_empty_text(self) -> None:
        client = PasteClient(base_url="https://example.com")
        with self.assertRaises(ValueError):
            client.create_paste("")

    def test_fetch_paste_returns_raw_text_without_listing(self) -> None:
        session = MagicMock()
        session.get.return_value = DummyResponse(text="hello")
        client = PasteClient(base_url="https://example.com", session=session)
        with patch.object(client, "list_pastes") as mocked_list:
            result = client.fetch_paste("abc", raw=True)
            self.assertEqual(result, "hello")
            mocked_list.assert_not_called()

    def test_fetch_paste_handles_listing_errors_gracefully(self) -> None:
        session = MagicMock()
        session.get.return_value = DummyResponse(text="hello")
        client = PasteClient(base_url="https://example.com", session=session)
        with patch.object(client, "list_pastes", side_effect=PasteError("nope")):
            result = client.fetch_paste("abc")
        self.assertEqual(result["id"], "abc")
        self.assertEqual(result["url"], "https://example.com/abc")
        self.assertEqual(result["text"], "hello")

    def test_list_pastes_uses_json_helper(self) -> None:
        session = MagicMock()
        session.get.return_value = DummyResponse(payload={"pastes": []})
        client = PasteClient(base_url="https://example.com", session=session)
        result = client.list_pastes()
        self.assertEqual(result, {"pastes": []})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
