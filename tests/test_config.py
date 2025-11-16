import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from icakad.config import DEFAULT_SHORTURL_BASE, Settings, load_settings


class SettingsTests(unittest.TestCase):
    def test_with_overrides_updates_only_provided_fields(self) -> None:
        base = Settings(shorturl_base="https://a", paste_base="https://b", token="one")
        updated = base.with_overrides(token="two", paste_base=None)
        self.assertEqual(updated.shorturl_base, "https://a")
        self.assertEqual(updated.paste_base, "https://b")
        self.assertEqual(updated.token, "two")

    def test_load_settings_reads_explicit_config_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "config.json"
            cfg.write_text(json.dumps({"token": "from-file", "shorturl_base": "https://file"}), encoding="utf-8")
            settings = load_settings(config_path=cfg)
        self.assertEqual(settings.token, "from-file")
        self.assertEqual(settings.shorturl_base, "https://file")
        self.assertEqual(settings.paste_base, DEFAULT_SHORTURL_BASE)

    def test_load_settings_raises_for_invalid_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "config.json"
            cfg.write_text("{invalid json}", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_settings(config_path=cfg)

    def test_environment_overrides_take_precedence(self) -> None:
        env = {
            "ICAKAD_SHORTURL_BASE": "https://env-short",
            "ICAKAD_PASTE_BASE": "https://env-paste",
            "ICAKAD_TOKEN": "env-token",
        }
        with patch.dict(os.environ, env, clear=False):
            settings = load_settings(token="direct-token")
        self.assertEqual(settings.shorturl_base, "https://env-short")
        self.assertEqual(settings.paste_base, "https://env-paste")
        self.assertEqual(settings.token, "direct-token")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
