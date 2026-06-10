#!/usr/bin/env python3
"""Test direct connectivity without proxy"""
import urllib.request
import os
import socket

# Remove proxy settings
for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(k, None)

# Install a no-proxy handler
proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)

targets = [
    ("HF", "https://huggingface.co/api/models?limit=1"),
    ("Koyeb", "https://api.koyeb.com/v1/instances"),
    ("Zeabur", "https://gateway.zeabur.com/graphql"),
    ("DockerHub", "https://hub.docker.com/v2/repositories/library/python/?page_size=1"),
]

for name, url in targets:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Python/3"}, method="GET")
        resp = opener.open(req, timeout=10)
        print(f"  {name}: {resp.status} OK")
    except urllib.error.HTTPError as e:
        print(f"  {name}: {e.code} (HTTP error, but reachable!)")
    except socket.timeout:
        print(f"  {name}: TIMEOUT")
    except Exception as e:
        print(f"  {name}: {type(e).__name__}: {str(e)[:80]}")
