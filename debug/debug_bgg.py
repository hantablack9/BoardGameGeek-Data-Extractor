import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


async def main():
    token = os.getenv("BGG_API_TOKEN")
    headers = {"User-Agent": "BGG-Extractor/1.0.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("Token found and added to headers.")
    else:
        print("Warning: No BGG_API_TOKEN found in environment.")

    urls = [
        "https://boardgamegeek.com/xmlapi2/thing?id=13",
        "https://api.geekdo.com/xmlapi2/thing?id=13",
    ]

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for url in urls:
            print(f"Testing {url}...")
            try:
                resp = await client.get(url)
                print(f"Status: {resp.status_code}")
                print(f"Body: {resp.text[:500]}")  # Print first 500 chars
            except Exception as e:
                print(f"Error: {e}")
            print("-" * 20)

        # Test Search Encoding
        print("Testing Search Encoding...")
        search_url = "https://boardgamegeek.com/xmlapi2/search"
        params = {"query": "Catan", "type": "boardgame"}
        resp = await client.get(search_url, params=params)
        print(f"Search Status: {resp.status_code}")
        print(f"Search URL: {resp.url}")


if __name__ == "__main__":
    asyncio.run(main())
