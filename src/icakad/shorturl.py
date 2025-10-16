# This is icakad.shorturl
# Usage: from icakad import shorturl
import requests

DEBUG = False
BASE = "https://linkove.icu"
HEADERS = {"Content-Type": "application/json","Authorization": f"Bearer {__all__['TOKEN']}"}

# === 1. Добавяне на нов линк ===
def add_link(slug, url):
    data = {"slug": slug, "url": url}
    r = requests.post(f"{BASE}/api", json=data, headers=HEADERS)
    if DEBUG:
        print("ADD:", r.status_code, r.json())
    return r.json()

# === 2. Редактиране (същото като добавяне – презаписва) ===
def edit_link(slug, new_url):
    data = {"slug": slug, "url": new_url}
    r = requests.post(f"{BASE}/api/{slug}", json=data, headers=HEADERS)
    if DEBUG:
        print("EDIT:", r.status_code, r.json())
    return r.json()

# === 3. Изтриване ===
def delete_link(slug):
    r = requests.delete(f"{BASE}/api/{slug}", headers=HEADERS)
    if DEBUG:
        print("DELETE:", r.status_code, r.json())
    return r.json()

# === 4. Листване на всички ===
def list_links():
    r = requests.get(f"{BASE}/api", headers=HEADERS)
    try:
        data = r.json()
    except ValueError:
        return {}

    # Може да е {"items":[...]} или директен списък
    if isinstance(data, dict):
        items = data.get("items", data.get("list", []))
    elif isinstance(data, list):
        items = data
    else:
        items = []

    links = {}
    for it in items:
        slug = it.get("key") or it.get("slug") or it.get("id") or it.get("name")
        url = it.get("url") or it.get("value")
        if slug and url:
            links[slug] = url

    if DEBUG:
        print(json.dumps(links, indent=2, ensure_ascii=False))

    return links
