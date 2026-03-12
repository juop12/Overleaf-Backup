
# Open the PyCharm terminal (bottom panel) and run:
#	pip install requests tqdm
#
# 💡 Small PyCharm tip:
# If PyCharm complains about imports, make sure you're using the same 
# interpreter where you installed the packages:
#	File → Settings → Python Interpreter
#

import requests
import os
import zipfile
import re
import json
import html
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

SESSION_COOKIE = "your_overleaf_session2_cookie"

BASE_URL = "https://www.overleaf.com"
DOWNLOAD_DIR = "overleaf_backup"
MAX_THREADS = 4
REQUEST_TIMEOUT = 60


def create_session(cookie):

    if not cookie:
        raise ValueError("Missing Overleaf cookie. Set SESSION_COOKIE in this file.")

    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": BASE_URL,
    })
    s.cookies.set("overleaf_session2", cookie, domain=".overleaf.com")
    return s

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def safe_name(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


def get_projects(session):

    print("Fetching project page...")

    r = session.get(f"{BASE_URL}/project", timeout=REQUEST_TIMEOUT)

    if r.status_code != 200:
        raise Exception("Failed to load project page (cookie expired?)")

    projects = []

    # Current Overleaf format: JSON stored in meta tag ol-prefetchedProjectsBlob.
    blob_match = re.search(
        r'<meta name="ol-prefetchedProjectsBlob"[^>]*content="([^"]*)"',
        r.text,
    )
    if blob_match:
        blob_json = html.unescape(blob_match.group(1))
        blob_data = json.loads(blob_json)
        projects = blob_data.get("projects", [])

    # Older Overleaf format fallback.
    if not projects:
        state_match = re.search(
            r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});\s*</script>',
            r.text,
            re.DOTALL,
        )
        if state_match:
            state_data = json.loads(state_match.group(1))
            projects = state_data.get("projects", {}).get("projects", [])

    if not projects:
        if "login" in r.text.lower() or "sign in" in r.text.lower():
            raise Exception("Cookie appears invalid or expired (redirected to login page).")
        raise Exception("Could not extract project list from Overleaf page.")

    print(f"Found {len(projects)} projects")

    return projects


def download_project(cookie, project, backup_dir):

    project_id = project.get("_id") or project.get("id")
    if not project_id:
        return False, "unknown", "missing project id"

    name = safe_name(project.get("name", "untitled"))

    folder = Path(backup_dir) / f"{name}_{project_id}"
    zip_path = Path(backup_dir) / f"{name}_{project_id}.zip"

    url = f"{BASE_URL}/project/{project_id}/download/zip"
    worker_session = create_session(cookie)

    try:
        r = worker_session.get(url, stream=True, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as ex:
        return False, name, f"request error: {ex}"

    if r.status_code != 200:
        return False, name, f"http {r.status_code}"

    try:
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

        folder.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(folder)
    except Exception as ex:
        if zip_path.exists():
            zip_path.unlink()
        return False, name, f"extract error: {ex}"
    finally:
        if zip_path.exists():
            zip_path.unlink()

    return True, name, "ok"


def main():

    session = create_session(SESSION_COOKIE)
    projects = get_projects(session)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(DOWNLOAD_DIR) / f"backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading projects...")

    success_count = 0
    failed = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(download_project, SESSION_COOKIE, p, backup_dir) for p in projects]

        for future in tqdm(as_completed(futures), total=len(futures)):
            ok, name, message = future.result()
            if ok:
                success_count += 1
            else:
                failed.append((name, message))

    print("\nBackup complete")
    print(f"Successful: {success_count}/{len(projects)}")

    if failed:
        print("Failed projects:")
        for name, error in failed:
            print(f"- {name}: {error}")

    metadata_path = backup_dir / "backup_summary.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "total_projects": len(projects),
                "successful": success_count,
                "failed": [{"name": n, "error": e} for n, e in failed],
            },
            f,
            indent=2,
        )

    print("Saved to:", backup_dir.resolve())
    print("Summary:", metadata_path.resolve())


if __name__ == "__main__":
    main()