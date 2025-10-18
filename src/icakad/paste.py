"""Thin client for the icakad paste worker JSON API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

import requests
from requests import Response, Session

DEFAULT_TIMEOUT = 10


class PasteError(RuntimeError):
    """Raised when the paste API reports a failure."""


@dataclass
class PasteClient:
    """Small helper around the paste worker endpoints."""

    base_url: str
    token: Optional[str] = None
    timeout: int = DEFAULT_TIMEOUT
    session: Optional[Session] = None
    _session: Session = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self._session = self.session or requests.Session()

    # ------------------------------------------------------------------ utils
    def _headers(self, *, content_type: Optional[str] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if content_type:
            headers["Content-Type"] = content_type
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _error_message(self, response: Response) -> str:
        body = (response.text or "").strip()
        if body:
            return f"{response.status_code}: {body}"
        return f"{response.status_code}: {response.reason}"

    def _json(self, response: Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise PasteError(self._error_message(response)) from exc
        try:
            return response.json()
        except ValueError as exc:
            raise PasteError("Paste API returned invalid JSON") from exc

    # ---------------------------------------------------------------- API ops
    def create_paste(
        self,
        text: str,
        *,
        paste_id: Optional[str] = None,
        ttl: Optional[int] = None,
        as_plaintext: bool = False,
    ) -> Dict[str, Any]:
        if not isinstance(text, str) or not text:
            raise ValueError("text must be a non-empty string")

        params: Dict[str, Any] = {}
        if paste_id:
            params["id"] = paste_id
        if ttl is not None:
            params["ttl"] = int(ttl)

        url = f"{self.base_url}/api/paste"

        if as_plaintext:
            headers = self._headers(content_type="text/plain; charset=utf-8")
            response = self._session.post(
                url,
                params=params,
                data=text,
                headers=headers,
                timeout=self.timeout,
            )
        else:
            headers = self._headers(content_type="application/json")
            response = self._session.post(
                url,
                params=params,
                json={"text": text},
                headers=headers,
                timeout=self.timeout,
            )
        return self._json(response)

    def fetch_paste(self, paste_id: str, *, raw: bool = False) -> Union[str, Dict[str, Any]]:
        url = f"{self.base_url}/raw/{paste_id}"
        response = self._session.get(
            url,
            headers=self._headers(),
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise PasteError(self._error_message(response)) from exc

        text = response.text
        if raw:
            return text

        details: Dict[str, Any] = {
            "id": paste_id,
            "url": f"{self.base_url}/{paste_id}",
            "text": text,
        }

        try:
            listing = self.list_pastes()
        except PasteError:
            return details

        pastes = listing.get("pastes") if isinstance(listing, dict) else None
        if isinstance(pastes, list):
            for item in pastes:
                if isinstance(item, dict) and item.get("id") == paste_id:
                    details.update({k: v for k, v in item.items() if k != "text"})
                    break
        return details

    def list_pastes(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/list"
        response = self._session.get(
            url,
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._json(response)
