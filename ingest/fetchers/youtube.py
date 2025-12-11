import os
import requests
import backoff
from typing import List, Dict, Any
from ingest.normalize import compute_ratios, normalize_title

class YouTubeFetcher:
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def search_videos(self, query: str = "n8n automation", region: str = "US", max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.api_key or self.api_key == "YOUR_YT_KEY":
            # Fallback for dev/test without key - return empty or mock? 
            # For now return empty to avoid errors, or maybe raise check
            print("Warning: No valid YOUTUBE_API_KEY found.")
            return []

        url = f"{self.BASE_URL}/search"
        params = {
            "part": "id,snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "regionCode": region,
            "key": self.api_key
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        items = data.get("items", [])
        video_ids = [item["id"]["videoId"] for item in items if "videoId" in item.get("id", {})]
        
        return self.get_video_details(video_ids, region)

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def get_video_details(self, video_ids: List[str], region: str) -> List[Dict[str, Any]]:
        if not video_ids:
            return []
            
        url = f"{self.BASE_URL}/videos"
        # Batching logic should happen upstream if > 50, but here we assume batch fits
        params = {
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": self.api_key
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data.get("items", []):
            stats = item["statistics"]
            snippet = item["snippet"]
            
            metrics = compute_ratios(
                stats.get("viewCount", 0),
                stats.get("likeCount", 0),
                stats.get("commentCount", 0)
            )
            
            # Canonical format
            results.append({
                "platform": "YouTube",
                "source_id": item["id"],
                "source_url": f"https://www.youtube.com/watch?v={item['id']}",
                "workflow": snippet["title"],
                "normalized_title": normalize_title(snippet["title"]),
                "country": region,
                "popularity_metrics": metrics,
                # "latest_metrics" will be same as popularity initially
                "collected_at": snippet["publishedAt"] # Approximate 'first_seen' or just payload time
            })
            
        return results
