"""HTTP клиенти за услугите на icakad."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, Union

import requests

__all__ = [
    "APIError",
    "BaseServiceClient",
    "ShortURLClient",
    "PasteClient",
    "normalise_shorturl_listing",
]


class APIError(RuntimeError):
    """Стандартна грешка за обвивките около HTTP услугите."""

    def __init__(self, message: str, *, status: Optional[int] = None, payload: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.payload = payload


@dataclass
class BaseServiceClient:
    """Базов клиент, който предоставя удобства за HTTP заявките."""

    base_url: str
    token: Optional[str] = None
    timeout: Union[float, Tuple[float, float]] = 15
    session: Optional[requests.Session] = None
    debug: bool = False
    default_headers: Mapping[str, str] = field(
        default_factory=lambda: {"Accept": "application/json"}
    )

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("base_url не може да бъде празно")
        self.base_url = self.base_url.rstrip("/")
        if self.session is None:
            self.session = requests.Session()

    # --- вътрешни помощници ---
    def _build_url(self, path: str = "") -> str:
        if not path:
            return self.base_url
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _compose_headers(self, headers: Optional[Mapping[str, str]]) -> Dict[str, str]:
        merged: Dict[str, str] = dict(self.default_headers)
        if headers:
            merged.update(headers)
        if self.token:
            merged.setdefault("Authorization", f"Bearer {self.token}")
        return merged

    def request(self, method: str, path: str = "", *, headers: Optional[Mapping[str, str]] = None, **kwargs: Any) -> Any:
        if self.session is None:
            self.session = requests.Session()
        url = self._build_url(path)
        prepared_headers = self._compose_headers(headers)
        if "timeout" not in kwargs and self.timeout:
            kwargs["timeout"] = self.timeout
        response = self.session.request(method.upper(), url, headers=prepared_headers, **kwargs)
        if self.debug:
            print(f"{method.upper()} {url} -> {response.status_code}")
        if response.status_code >= 400:
            payload: Any
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            raise APIError(
                f"Заявката към {url} се провали със статус {response.status_code}",
                status=response.status_code,
                payload=payload,
            )
        content_type = response.headers.get("Content-Type", "")
        if "json" in content_type:
            try:
                return response.json()
            except ValueError:
                raise APIError("Сървърът върна невалиден JSON", payload=response.text)
        return response.text


class ShortURLClient(BaseServiceClient):
    """Клиент за услугата за кратки линкове."""

    def create(self, *, slug: str, url: str) -> Mapping[str, Any]:
        payload = {"slug": slug, "url": url}
        return self.request("post", "", json=payload)

    def update(self, *, slug: str, url: str) -> Mapping[str, Any]:
        payload = {"slug": slug, "url": url}
        return self.request("post", f"/{slug}", json=payload)

    def delete(self, *, slug: str) -> Mapping[str, Any]:
        return self.request("delete", f"/{slug}")

    def list(self) -> Any:
        return self.request("get", "")


def normalise_shorturl_listing(raw: Any) -> Dict[str, str]:
    """Опитва да нормализира произволен JSON от списъчния endpoint."""

    if raw is None:
        return {}

    if isinstance(raw, Mapping):
        # често JSON е {"items": [...]} или {"data": [...]}
        for key in ("items", "data", "list"):
            value = raw.get(key)
            if isinstance(value, list):
                return _items_to_dict(value)
        # може вече да е словар slug->url
        return {str(k): str(v) for k, v in raw.items() if isinstance(k, str)}

    if isinstance(raw, list):
        return _items_to_dict(raw)

    return {}


def _items_to_dict(items: Iterable[Any]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for entry in items:
        if not isinstance(entry, Mapping):
            continue
        slug = (
            entry.get("slug")
            or entry.get("key")
            or entry.get("id")
            or entry.get("name")
        )
        url = entry.get("url") or entry.get("value") or entry.get("target")
        if slug and url:
            result[str(slug)] = str(url)
    return result


class PasteClient(BaseServiceClient):
    """Клиент за paste услугата."""

    def create(
        self,
        *,
        content: str,
        title: Optional[str] = None,
        syntax: Optional[str] = None,
        expires_in: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Mapping[str, Any]:
        payload: Dict[str, Any] = {"content": content}
        if title:
            payload["title"] = title
        if syntax:
            payload["syntax"] = syntax
        if expires_in:
            payload["expires_in"] = expires_in
        if password:
            payload["password"] = password
        return self.request("post", "", json=payload)

    def fetch(self, paste_id: str) -> Any:
        return self.request("get", f"/{paste_id}")

    def delete(self, paste_id: str) -> Any:
        return self.request("delete", f"/{paste_id}")
