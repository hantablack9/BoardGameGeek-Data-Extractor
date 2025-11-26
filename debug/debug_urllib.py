import urllib.error
import urllib.request


def test_url(url):
    print(f"Testing {url}...")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.status}")
            print(f"Body: {response.read().decode('utf-8')[:200]}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(f"Headers: {e.headers}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)


if __name__ == "__main__":
    test_url("https://boardgamegeek.com/xmlapi2/thing?id=13")
    test_url("https://api.geekdo.com/xmlapi2/thing?id=13")
    test_url("http://boardgamegeek.com/xmlapi2/thing?id=13")
