import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from icakad.common import (
    comma_separated,
    ensure_parent,
    print_json,
    read_text_file,
    resolve_text_input,
    write_json,
    write_text,
)


class CommonHelpersTests(unittest.TestCase):
    def test_ensure_parent_and_write_json_create_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "data.json"
            ensure_parent(target)
            self.assertTrue(target.parent.exists())
            written = write_json({"key": "value"}, target)
            self.assertEqual(written, target.resolve())
            payload = json.loads(written.read_text(encoding="utf-8"))
            self.assertEqual(payload, {"key": "value"})

    def test_write_text_and_read_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "note.txt"
            write_text("hello world", target)
            self.assertEqual(read_text_file(target), "hello world")

    def test_resolve_text_input_prefers_inline_value(self) -> None:
        resolved = resolve_text_input(text="hello\n")
        self.assertEqual(resolved, "hello")

    def test_resolve_text_input_reads_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "body.txt"
            path.write_text("file contents", encoding="utf-8")
            resolved = resolve_text_input(text_file=path)
            self.assertEqual(resolved, "file contents")

    def test_resolve_text_input_rejects_empty_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.txt"
            path.write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                resolve_text_input(text_file=path)

    def test_print_json_emits_pretty_output(self) -> None:
        buffer = StringIO()
        with redirect_stdout(buffer):
            print_json({"key": "✓"})
        self.assertEqual(buffer.getvalue().strip(), json.dumps({"key": "✓"}, indent=2, ensure_ascii=False))

    def test_comma_separated_casts_values_to_string(self) -> None:
        sentence = comma_separated(["alpha", 42, "omega"])
        self.assertEqual(sentence, "alpha, 42, omega")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
