import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from icakad import cli


class CLITests(unittest.TestCase):
    def test_main_invokes_shorturl_add(self) -> None:
        with patch("icakad.cli.add_short_link", return_value={"ok": True}) as mocked_add:
            rc = cli.main(["shorturl", "add", "demo", "https://example.com", "--quiet"])
        self.assertEqual(rc, 0)
        mocked_add.assert_called_once_with(
            "demo",
            "https://example.com",
            save_to=None,
            config_path=None,
            token=None,
            base_url=None,
        )

    def test_paste_create_flows_through_resolve_text_input(self) -> None:
        with patch("icakad.cli.resolve_text_input", return_value="BODY") as mocked_resolve, patch(
            "icakad.cli.create_paste", return_value={"ok": True}
        ) as mocked_create:
            rc = cli.main(["paste", "create", "--text", "ignored", "--plain", "--quiet"])

        self.assertEqual(rc, 0)
        mocked_resolve.assert_called_once_with(text="ignored", text_file=None)
        mocked_create.assert_called_once_with(
            text="BODY",
            paste_id=None,
            ttl=None,
            as_plaintext=True,
            save_to=None,
            config_path=None,
            token=None,
            base_url=None,
        )

    def test_paste_get_raw_prints_plain_text(self) -> None:
        with patch("icakad.cli.fetch_paste", return_value="hello") as mocked_fetch:
            stdout = StringIO()
            with redirect_stdout(stdout):
                rc = cli.main(["paste", "get", "abc", "--raw"])

        self.assertEqual(rc, 0)
        mocked_fetch.assert_called_once()
        self.assertEqual(stdout.getvalue().strip(), "hello")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
