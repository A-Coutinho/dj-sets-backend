import base64
import os
import time
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

DROPBOX_CLIENT_ID = os.environ["DROPBOX_CLIENT_ID"]
DROPBOX_CLIENT_SECRET = os.environ["DROPBOX_CLIENT_SECRET"]
DROPBOX_REFRESH_TOKEN = os.environ["DROPBOX_REFRESH_TOKEN"]

_access_token = None
_expires_at = 0
_files_cache = None
_files_cache_ts = 0
FILES_CACHE_TTL = 6000


def get_access_token() -> str:
    global _access_token, _expires_at
    if _access_token and time.time() < _expires_at:
        return _access_token

    resp = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": DROPBOX_REFRESH_TOKEN,
            "client_id": DROPBOX_CLIENT_ID,
            "client_secret": DROPBOX_CLIENT_SECRET,
        },
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to refresh token")

    data = resp.json()
    _access_token = data["access_token"]
    _expires_at = time.time() + data.get("expires_in", 3600)
    return _access_token

def list_files():
    global _files_cache, _files_cache_ts
    start_time = time.perf_counter()
    now = time.time()

    if _files_cache and now - _files_cache_ts < FILES_CACHE_TTL:
        print(f"[list_files] Returned from cache in {time.perf_counter() - start_time:.3f}s")
        return _files_cache

    token = get_access_token()
    resp = requests.post(
        "https://api.dropboxapi.com/2/files/list_folder",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"path": "", "recursive": False},
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=resp.text)

    entries = resp.json().get("entries", [])
    mp3_files = [f for f in entries if f[".tag"] == "file" and f["name"].lower().endswith(".mp3")]
    image_files = [f for f in entries if f[".tag"] == "file" and f["name"].lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    txt_files = {f["name"].lower(): f for f in entries if f[".tag"] == "file" and f["name"].lower().endswith(".txt")}

    cover_url = get_download_link(image_files[0]["path_lower"]) if image_files else None
    b64_data = base64.b64encode(requests.get(cover_url).content).decode()
    print(b64_data)

    result = []
    for f in mp3_files:
        tracklist_text = None
        txt_name = f["name"].rsplit(".", 1)[0].lower() + ".txt"
        if txt_name in txt_files:
            txt_path = txt_files[txt_name]["path_lower"]
            txt_resp = requests.post(
                "https://content.dropboxapi.com/2/files/download",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Dropbox-API-Arg": f'{{"path": "{txt_path}"}}'
                },
            )
            if txt_resp.status_code == 200:
                tracklist_text = txt_resp.text

        result.append({
            "name": f["name"],
            "path_lower": f["path_lower"],
            "link": get_download_link(f["path_lower"]),
            "cover": f"data:image/jpeg;base64,{b64_data}",
            "tracklist": tracklist_text,
            "is_downloadable": f.get("is_downloadable", False),
            "id": f.get("id"),
        })

    _files_cache = result
    _files_cache_ts = now
    print(f"[list_files] Executed in {time.perf_counter() - start_time:.3f}s")
    return result

def get_download_link(path: str) -> str:
    token = get_access_token()
    resp = requests.post(
        "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"path": path},
    )
    if resp.status_code == 409:
        resp = requests.post(
            "https://api.dropboxapi.com/2/sharing/list_shared_links",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"path": path},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=resp.text)

    data = resp.json()
    if "url" in data:
        link = data["url"]
    elif "links" in data and len(data["links"]) > 0:
        link = data["links"][0]["url"]
    else:
        raise HTTPException(status_code=500, detail="No shared link found")

    link = link.replace("?dl=0", "?dl=1")
    link = link.replace("&dl=0", "&dl=1")
    return link
