import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from icakad.config import load_settings
from icakad.paste import PasteClient
from icakad.shorturl import ShortURLClient
from icakad import (
    AI,
    create_paste,
    delete_short_link,
    fetch_paste,
    list_short_links,
    update_short_link,
)


def make_response(*, json_data=None, text="", status=200):
    response = MagicMock()
    response.status_code = status

    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError("error")
    else:
        response.raise_for_status.return_value = None

    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.side_effect = ValueError("no json")

    response.text = text
    return response


class SettingsTests(unittest.TestCase):
    def test_load_settings_from_file_and_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "icakad.json"
            config_path.write_text(json.dumps({"token": "file-token"}), encoding="utf-8")

            os.environ["ICAKAD_SHORTURL_BASE"] = "https://env-short.test"
            try:
                settings = load_settings(
                    config_path=config_path,
                    paste_base="https://override-paste.test",
                )
            finally:
                os.environ.pop("ICAKAD_SHORTURL_BASE", None)

        self.assertEqual(settings.token, "file-token")
        self.assertEqual(settings.shorturl_base, "https://env-short.test")
        self.assertEqual(settings.paste_base, "https://override-paste.test")


class ShortURLClientTests(unittest.TestCase):
    def test_client_operations_use_expected_routes(self):
        session = MagicMock()
        base = "https://linkove.icu"
        session.post.side_effect = [
            make_response(json_data={"ok": True}),
            make_response(json_data={"ok": True}),
        ]
        session.delete.return_value = make_response(json_data={"ok": True})
        session.get.return_value = make_response(
            json_data={"items": [{"slug": "demo", "url": "https://example.com"}]}
        )

        client = ShortURLClient(base_url=base, token="token", session=session)
        client.add_link("demo", "https://example.com")
        session.post.assert_called_with(
            f"{base}/api",
            json={"slug": "demo", "url": "https://example.com"},
            headers={"Content-Type": "application/json", "Authorization": "Bearer token"},
            timeout=10,
        )

        client.edit_link("demo", "https://example.com")
        session.post.assert_called_with(
            f"{base}/api/demo",
            json={"slug": "demo", "url": "https://example.com"},
            headers={"Content-Type": "application/json", "Authorization": "Bearer token"},
            timeout=10,
        )

        client.delete_link("demo")
        session.delete.assert_called_with(
            f"{base}/api/demo",
            headers={"Content-Type": "application/json", "Authorization": "Bearer token"},
            timeout=10,
        )

        links = client.list_links()
        self.assertEqual(links, {"demo": "https://example.com"})


class PasteClientTests(unittest.TestCase):
    def test_fetch_paste_merges_metadata(self):
        session = MagicMock()
        base = "https://linkove.icu"
        session.post.return_value = make_response(json_data={"ok": True, "id": "abc", "url": f"{base}/abc"})
        session.get.side_effect = [
            make_response(text="hello"),
            make_response(json_data={"ok": True, "pastes": [{"id": "abc", "text": "hello"}]}),
        ]

        client = PasteClient(base_url=base, session=session)
        created = client.create_paste("hello")
        self.assertTrue(created["ok"])
        fetched = client.fetch_paste("abc")
        self.assertEqual(fetched["text"], "hello")
        self.assertEqual(fetched["id"], "abc")
        self.assertEqual(fetched["url"], f"{base}/abc")


class HighLevelHelpersTests(unittest.TestCase):
    def test_list_short_links_can_write_file(self):
        fake_client = MagicMock()
        fake_client.list_links.return_value = {"demo": "https://example.com"}
        with tempfile.TemporaryDirectory() as tmp, patch("icakad._client_from_settings", return_value=fake_client):
            output = Path(tmp) / "links.json"
            data = list_short_links(save_to=output)
            self.assertEqual(data, {"demo": "https://example.com"})
            stored = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(stored, data)

    def test_fetch_paste_raw_output(self):
        fake_client = MagicMock()
        fake_client.fetch_paste.return_value = "hello world"
        with tempfile.TemporaryDirectory() as tmp, patch("icakad._paste_client_from_settings", return_value=fake_client):
            output = Path(tmp) / "paste.txt"
            result = fetch_paste("abc", raw=True, save_to=output)
            self.assertEqual(result, "hello world")
            self.assertEqual(output.read_text(encoding="utf-8"), "hello world")

    def test_create_paste_uses_text_file(self):
        fake_client = MagicMock()
        fake_client.create_paste.return_value = {"ok": True}
        with tempfile.TemporaryDirectory() as tmp, patch("icakad._paste_client_from_settings", return_value=fake_client):
            text_file = Path(tmp) / "note.txt"
            text_file.write_text("Hello", encoding="utf-8")
            result = create_paste(text_file=text_file)
            self.assertTrue(result["ok"])
            fake_client.create_paste.assert_called_with("Hello", paste_id=None, ttl=None, as_plaintext=False)

    def test_update_and_delete_short_link(self):
        fake_client = MagicMock()
        fake_client.edit_link.return_value = {"ok": True}
        fake_client.delete_link.return_value = {"ok": True}

        with patch("icakad._client_from_settings", return_value=fake_client):
            update = update_short_link("demo", "https://example.com")
            delete = delete_short_link("demo")
        self.assertTrue(update["ok"])
        self.assertTrue(delete["ok"])


class AITests(unittest.TestCase):
    def test_ask_posts_prompt_to_worker(self):
        with patch("icakad.ai.requests.post") as mocked_post:
            mocked_post.return_value = make_response(
                json_data={"response": "Здрасти"}
            )
            reply = AI.ask("Hello from Pythonista")

        self.assertEqual(reply, "Здрасти")
        mocked_post.assert_called_with(
            "https://llama.icakad.workers.dev/",
            json={"messages": [{"role": "user", "content": "Hello from Pythonista"}]},
            headers={"Content-Type": "application/json"},
            timeout=20.0,
        )


if __name__ == "__main__":
    unittest.main()
