#!/usr/bin/env python3
"""Quick test - replace TOKEN with your actual token below, then run: python3 figma_test.py"""

# TODO: Replace with your token from Figma (Settings -> Account -> Personal access tokens)
TEST_TOKEN = "your-token-here"

import asyncio
import httpx

async def test():
    print(f"Token: {TEST_TOKEN[:20]}...")

    client = httpx.AsyncClient(
        headers={"X-Figma-Token": TEST_TOKEN},
        timeout=10.0
    )

    try:
        # Try to fetch a test file (will 404 but proves connection works)
        resp = await client.get("https://www.figma.com/design/vLcVO8YQvAu4G8QgSVtX2s/An-Educational-APP-Authentication---Onboarding-Mobile-UI--Community-?node-id=203-966&t=nVTHBFrYZxGINutH-4")
        print(f"Status: {resp.status_code}")

        if resp.status_code == 404:
            print("✓ API connection works!")
        elif resp.status_code == 403:
            print("✗ Token invalid - check your Figma token")
        elif resp.status_code == 200:
            print("✓ Got valid file data!")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    if TEST_TOKEN == "YOUR_TOKEN_HERE":
        print("Please edit this file and replace TEST_TOKEN with your Figma token")
    else:
        asyncio.run(test())