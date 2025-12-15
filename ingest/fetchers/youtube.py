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
            print("Warning: No valid YOUTUBE_API_KEY found. Returning MOCK data for verification.")
            from datetime import datetime, timedelta
            # Mock data for demonstration
            return [
                {
                    "platform": "YouTube",
                    "source_id": "mock_yt_1",
                    "source_url": "https://www.youtube.com/watch?v=mock1",
                    "workflow": "Automating Email with n8n (Mock)",
                    "normalized_title": "automating email with n8n",
                    "country": region,
                    "popularity_metrics": {
                        "views": 15000,
                        "likes": 500,
                        "comments": 50,
                        "like_to_view_ratio": 0.033,
                        "comment_to_view_ratio": 0.003
                    },
                    "collected_at": (datetime.now() - timedelta(days=2)).isoformat()
                },
                {
                    "platform": "YouTube",
                    "source_id": "mock_yt_2",
                    "source_url": "https://www.youtube.com/watch?v=mock2",
                    "workflow": "n8n Webhook Tutorial (Mock)",
                    "normalized_title": "n8n webhook tutorial",
                    "country": region,
                    "popularity_metrics": {
                        "views": 8200,
                        "likes": 300,
                        "comments": 20,
                        "like_to_view_ratio": 0.036,
                        "comment_to_view_ratio": 0.002
                    },
                    "collected_at": (datetime.now() - timedelta(days=5)).isoformat()
                }
            ]

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
