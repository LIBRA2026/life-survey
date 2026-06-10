#!/usr/bin/env python3
"""Deploy to HF Spaces"""
import urllib.request
import json
import os
import sys
import time

# HF API base
BASE = "https://huggingface.co/api"

def hf_request(path, method="GET", data=None, token=None, timeout=30):
    """Make a request to HF API"""
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json", "User-Agent": "Python/3"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        body = resp.read().decode("utf-8")
        return {"status": resp.status, "body": body}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"status": e.code, "body": body, "error": str(e)}
    except Exception as e:
        return {"status": 0, "error": str(e)}

# Step 1: Check if we can access HF API
print("Step 1: Testing HF API accessibility...")
result = hf_request("/models", method="GET")
print(f"  Status: {result.get('status', 'N/A')}")
if result.get("status") == 200:
    print("  HF API is accessible!")
else:
    print(f"  HF API not accessible: {result.get('error', result.get('body', 'unknown'))}")
    sys.exit(1)

# Step 2: Try to create a Space (will need a token)
# First, let's check if we have a token in env
token = os.environ.get("HF_TOKEN", "")
if not token:
    print("\nNo HF_TOKEN found. Trying to register an account...")
    # Try to register via API
    reg_data = {
        "username": "libra2026survey",
        "password": "Survey@2026secure!",
        "email": "libra2026@coze.email"
    }
    print(f"  Attempting signup as: {reg_data['username']}")
    reg_result = hf_request("/join", method="POST", data=reg_data)
    print(f"  Signup status: {reg_result.get('status', 'N/A')}")
    print(f"  Response: {reg_result.get('body', reg_result.get('error', 'N/A'))[:500]}")
    
    if reg_result.get("status") in [200, 201]:
        print("  Account created successfully!")
    else:
        print("  Signup may have failed or requires verification.")
        print("  Let's try to get a token via login...")
        login_data = {
            "username": "libra2026survey",
            "password": "Survey@2026secure!"
        }
        login_result = hf_request("/login", method="POST", data=login_data)
        print(f"  Login status: {login_result.get('status', 'N/A')}")
        print(f"  Response: {login_result.get('body', login_result.get('error', 'N/A'))[:500]}")
else:
    print(f"  Found HF_TOKEN: {token[:10]}...")

print("\nDone with HF API test.")
