#!/usr/bin/env python3
import urllib.request
import socket

targets = [
    ("HF API", "https://huggingface.co/api"),
    ("Koyeb API", "https://api.koyeb.com/v1"),
    ("Zeabur", "https://gateway.zeabur.com"),
    ("Docker Hub", "https://hub.docker.com"),
    ("GHCR", "https://ghcr.io"),
]

for name, url in targets:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Python/3"}, method="GET")
        resp = urllib.request.urlopen(req, timeout=8)
        print(f"  {name}: {resp.status} OK")
    except urllib.error.HTTPError as e:
        print(f"  {name}: {e.code} (HTTP error, but reachable)")
    except socket.timeout:
        print(f"  {name}: TIMEOUT (unreachable)")
    except Exception as e:
        print(f"  {name}: {type(e).__name__}: {str(e)[:100]}")
