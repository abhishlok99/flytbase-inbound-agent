"""Keyless real-time news: Google News RSS. No API key, no cost -- chosen
deliberately so the system's research quality never depends on paid access."""
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

HEADERS = {"User-Agent": "Mozilla/5.0 (FlytBase-BDR-Hackathon-Research)"}


def search_news(query: str, max_results: int = 8) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:max_results]:
            items.append({
                "title": (item.findtext("title") or "").strip(),
                "link": (item.findtext("link") or "").strip(),
                "pubDate": (item.findtext("pubDate") or "").strip(),
                "source": (item.findtext("source") or "").strip(),
            })
        return items
    except Exception as e:
        return [{"error": str(e), "note": "news fetch unreachable at run time"}]
