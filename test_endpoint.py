#!/usr/bin/env python3
"""Test Discord interactions endpoint"""

import json
import requests

# Discord PING request
ping_data = {"type": 1}

# Your Railway URL
url = "https://discord-arxiv-bot-production.up.railway.app/interactions"

# Test the endpoint
try:
    response = requests.post(
        url,
        json=ping_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("type") == 1:
            print("✅ PING test successful!")
        else:
            print("❌ Wrong response type")
    else:
        print("❌ Request failed")
        
except Exception as e:
    print(f"❌ Error: {e}")