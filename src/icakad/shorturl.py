"""Клиент за Cloudflare worker-а, който управлява късите линкове."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import requests
from requests import Response, Session

DEFAULT_TIMEOUT = 10


class ShortURLError(RuntimeError):
    """Фатална грешка, върната от shorturl API."""


def _extract_items(payload: object) -> List[Dict[str, object]]:
    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("list")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


@dataclass
class ShortURLClient:
    """Лек HTTP клиент за CRUD операции върху shorturl работника."""

    base_url: str
    token: Optional[str] = None
    timeout: int = DEFAULT_TIMEOUT
    session: Optional[Session] = None
    _session: Session = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self._session = self.session or requests.Session()

    # ---------------------------------------------------------------- utils
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, **kwargs: object) -> Response:
        url = f"{self.base_url}{path}"
        session_method = getattr(self._session, method)
        response = session_method(
            url,
            headers=self._headers(),
            timeout=self.timeout,
            **kwargs,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ShortURLError(f"{response.status_code}: {response.text}") from exc
        return response

    # ----------------------------------------------------------- API methods
    def add_link(self, slug: str, url: str) -> Dict[str, object]:
        payload = {"slug": slug, "url": url}
        response = self._request("post", "/api", json=payload)
        return self._json(response)

    def edit_link(self, slug: str, url: str) -> Dict[str, object]:
        payload = {"slug": slug, "url": url}
        response = self._request("post", f"/api/{slug}", json=payload)
        return self._json(response)

    def delete_link(self, slug: str) -> Dict[str, object]:
        response = self._request("delete", f"/api/{slug}")
        return self._json(response)

    def list_links(self) -> Dict[str, str]:
        response = self._request("get", "/api")
        try:
            payload = response.json()
        except ValueError as exc:
            raise ShortURLError("ShortURL API returned invalid JSON") from exc

        links: Dict[str, str] = {}
        for item in _extract_items(payload):
            slug = (
                item.get("slug")
                or item.get("key")
                or item.get("id")
                or item.get("name")
            )
            url = item.get("url") or item.get("value")
            if isinstance(slug, str) and isinstance(url, str):
                links[slug] = url
        return links

    # --------------------------------------------------------------- helpers
    def _json(self, response: Response) -> Dict[str, object]:
        try:
            data = response.json()
        except ValueError as exc:
            raise ShortURLError("ShortURL API returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise ShortURLError("ShortURL API returned an unexpected payload")
        return data
