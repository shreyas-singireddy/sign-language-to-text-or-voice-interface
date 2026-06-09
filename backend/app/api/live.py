import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter
from app.data.live_feed import LIVE_FEED

router = APIRouter()

ONLINE_SOURCE = 'https://api.quotable.io/random'


def fetch_online_live_data() -> list[dict[str, str]]:
    request = Request(ONLINE_SOURCE, headers={'User-Agent': 'SignBridgeAI/1.0'})
    with urlopen(request, timeout=5) as response:
        payload = json.loads(response.read().decode('utf-8'))
        return [
            {
                'id': f"online-{payload.get('id', 'quote')}",
                'title': payload.get('content', 'Live update from the web'),
                'description': f"— {payload.get('author', 'Unknown')}"
            }
        ]


@router.get('/live-data')
async def live_data() -> dict[str, object]:
    try:
        items = fetch_online_live_data()
        return {'source': 'online', 'items': items}
    except (HTTPError, URLError, OSError, ValueError):
        return {'source': 'offline', 'items': LIVE_FEED}
