import asyncio
import os

from dotenv import load_dotenv

from bgg_extractor.client import BGGClient

load_dotenv()


async def main():
    print(f"Token in env: {os.getenv('BGG_API_TOKEN')}")

    async with BGGClient() as client:
        print(f"Client token: {client.token}")
        try:
            print("Fetching thing 13...")
            thing = await client.get_thing([13])
            print(f"Success! Thing: {thing.items[0].name}")
        except Exception as e:
            print(f"Error fetching thing: {e}")

        try:
            print("Searching for Catan...")
            search_results = await client.search("Catan", type="boardgame")
            print(f"Success! Found {len(search_results.items)} items.")
            if search_results.items:
                print(f"First item: {search_results.items[0].name} ({search_results.items[0].type})")
        except Exception as e:
            print(f"Error searching: {e}")

        try:
            print("Fetching user ScottAlden...")
            user = await client.get_user("ScottAlden")
            print(f"Success! User: {user.name} (ID: {user.id})")
        except Exception as e:
            print(f"Error fetching user: {e}")


if __name__ == "__main__":
    asyncio.run(main())
