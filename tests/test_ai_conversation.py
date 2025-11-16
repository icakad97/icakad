"""Тестове за симулиран разговор между два AI клиента."""

from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Dict, List

from icakad import ai as ai_module
from icakad.ai import AI


class _DummyResponse:
    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Dict[str, str]:
        return {"response": self._reply}


class _DummySession:
    def __init__(self) -> None:
        self.turn = 0
        self.posts: List[Dict[str, Any]] = []

    def post(self, url: str, *, json: Dict[str, Any], headers, timeout):
        self.posts.append({"url": url, "payload": json, "headers": headers, "timeout": timeout})
        prompt = json["messages"][-1]["content"]
        responder = "AI-2" if self.turn % 2 == 0 else "AI-1"
        listener = "AI-1" if responder == "AI-2" else "AI-2"
        reply = f"{responder} към {listener}: получих '{prompt}'"
        self.turn += 1
        return _DummyResponse(reply)


class AIConversationTests(unittest.TestCase):
    def test_two_ai_clients_exchange_ten_messages(self) -> None:
        session = _DummySession()
        transcript: List[str] = []
        prompt = "AI-1 към AI-2: Здрасти!"
        stdout_buffer = StringIO()

        with redirect_stdout(stdout_buffer):
            for _ in range(10):
                reply = AI.ask(prompt, session=session)
                transcript.append(reply)
                print(reply)
                prompt = reply

        printed_lines = [line for line in stdout_buffer.getvalue().splitlines() if line]
        self.assertEqual(transcript, printed_lines)
        self.assertEqual(len(transcript), 10)

        expected_speakers = ["AI-2", "AI-1"] * 5
        for reply, speaker in zip(transcript, expected_speakers):
            self.assertTrue(reply.startswith(speaker))

        self.assertEqual(len(session.posts), 10)
        for recorded in session.posts:
            self.assertEqual(recorded["url"], "https://llama.icakad.workers.dev/")
            self.assertIn("messages", recorded["payload"])
            self.assertEqual(recorded["headers"], {"Content-Type": "application/json"})
            self.assertEqual(recorded["timeout"], 20.0)

    def test_module_level_ask_is_available(self) -> None:
        session = _DummySession()
        reply = ai_module.ask("Здравей", session=session)

        self.assertIsInstance(reply, str)
        self.assertEqual(len(session.posts), 1)
        recorded = session.posts[0]
        self.assertEqual(recorded["payload"]["messages"], [{"role": "user", "content": "Здравей"}])


if __name__ == "__main__":
    unittest.main()
