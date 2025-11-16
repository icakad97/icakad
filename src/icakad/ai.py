"""Минимален клиент към LLM работника на icakad."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

import requests


Message = Mapping[str, str]

__all__ = ["AI", "ask"]


class AI:
    """Обвивка за изпращане на съобщения към LLM през HTTP."""

    default_url: str = "https://llama.icakad.workers.dev/"
    default_timeout: float = 20.0
    _default_headers: Dict[str, str] = {"Content-Type": "application/json"}

    @classmethod
    def ask(
        cls,
        prompt: str,
        *,
        messages: Optional[Iterable[Message]] = None,
        url: Optional[str] = None,
        timeout: Optional[float] = None,
        session: Optional[requests.sessions.Session] = None,
    ) -> str:
        """Изпраща *prompt* и връща отговора от работника."""

        payload = {"messages": cls._build_messages(prompt, messages)}
        target_url = (url or cls.default_url).rstrip("/") + "/"
        request_timeout = cls.default_timeout if timeout is None else float(timeout)

        sender = session.post if session is not None else requests.post
        response = sender(
            target_url,
            json=payload,
            headers=dict(cls._default_headers),
            timeout=request_timeout,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, MutableMapping) or "response" not in data:
            raise ValueError("LLM worker returned an unexpected payload")
        return str(data["response"])

    @staticmethod
    def _build_messages(
        prompt: str,
        messages: Optional[Iterable[Message]],
    ) -> List[Dict[str, str]]:
        if messages is not None:
            normalized: List[Dict[str, str]] = []
            for item in messages:
                if not isinstance(item, Mapping):
                    raise TypeError("messages must contain mapping items")
                role = item.get("role")
                content = item.get("content")
                if role is None or content is None:
                    raise ValueError("Each message requires 'role' and 'content'")
                normalized.append({"role": str(role), "content": str(content)})
            if not normalized:
                raise ValueError("messages cannot be empty")
            return normalized

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        return [{"role": "user", "content": prompt}]


def ask(
    prompt: str,
    *,
    messages: Optional[Iterable[Message]] = None,
    url: Optional[str] = None,
    timeout: Optional[float] = None,
    session: Optional[requests.sessions.Session] = None,
) -> str:
    """Улеснена обвивка за :meth:`AI.ask` достъпна на ниво модул."""

    return AI.ask(
        prompt,
        messages=messages,
        url=url,
        timeout=timeout,
        session=session,
    )
