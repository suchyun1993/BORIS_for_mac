#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import subprocess
import urllib.parse
import urllib.request
from urllib.error import HTTPError


def get_github_token() -> str:
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        text=True,
        capture_output=True,
        timeout=15,
    )
    if proc.returncode != 0:
        raise RuntimeError("git credential fill failed")

    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("no GitHub token/password available via git credential helper")


def request_json(method: str, url: str, headers: dict, data: dict | None = None, timeout: int = 60) -> dict:
    payload = None
    req_headers = dict(headers)
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=payload, method=method, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--asset", required=True)
    args = parser.parse_args()

    if not os.path.isfile(args.asset):
        raise SystemExit(f"asset not found: {args.asset}")

    token = get_github_token()
    api_base = f"https://api.github.com/repos/{args.owner}/{args.repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "boris-for-mac-release-publisher",
    }

    print("Checking release...")
    try:
        release = request_json("GET", f"{api_base}/releases/tags/{urllib.parse.quote(args.tag)}", headers=headers)
        print("Found existing release")
    except HTTPError as err:
        if err.code != 404:
            raise
        release = request_json(
            "POST",
            f"{api_base}/releases",
            headers=headers,
            data={
                "tag_name": args.tag,
                "name": args.name,
                "body": args.body,
                "draft": False,
                "prerelease": False,
            },
        )
        print("Created release")

    release_id = release["id"]
    release = request_json(
        "PATCH",
        f"{api_base}/releases/{release_id}",
        headers=headers,
        data={"name": args.name, "body": args.body},
    )

    asset_name = os.path.basename(args.asset)
    for item in release.get("assets", []) or []:
        if item.get("name") == asset_name:
            req = urllib.request.Request(
                f"{api_base}/releases/assets/{item['id']}",
                headers=headers,
                method="DELETE",
            )
            with urllib.request.urlopen(req, timeout=60):
                pass
            print("Deleted existing asset")
            break

    upload_url = release["upload_url"].split("{")[0]
    with open(args.asset, "rb") as f:
        data = f.read()

    content_type = mimetypes.guess_type(asset_name)[0] or "application/octet-stream"
    req = urllib.request.Request(
        f"{upload_url}?name={urllib.parse.quote(asset_name)}",
        data=data,
        method="POST",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "boris-for-mac-release-publisher",
            "Content-Type": content_type,
        },
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        uploaded = json.loads(resp.read().decode("utf-8"))

    print(f"Uploaded asset: {uploaded.get('name')}")
    print(f"Release URL: {release.get('html_url')}")


if __name__ == "__main__":
    main()
