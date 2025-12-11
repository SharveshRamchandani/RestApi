import os
import requests
import backoff
from typing import List, Dict, Any
from datetime import datetime
from ingest.normalize import normalize_title, compute_ratios

class DiscourseFetcher:
    def __init__(self, base_url: str = None, api_key: str = None, api_user: str = None):
        self.base_url = base_url or os.getenv("DISCOURSE_BASE_URL", "https://forum.n8n.io")
        self.api_key = api_key or os.getenv("DISCOURSE_API_KEY")
        self.api_user = api_user or os.getenv("DISCOURSE_API_USER")

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key and self.api_user:
            h["Api-Key"] = self.api_key
            h["Api-Username"] = self.api_user
        return h

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def fetch_latest_topics(self, pages: int = 3) -> List[Dict[str, Any]]:
        results = []
        # Discourse pagination usually by page query param? Or 'more_topics_url'. 
        # Standard endpoint: /latest.json?page=X
        
        for page in range(pages):
            url = f"{self.base_url}/latest.json"
            params = {"page": page} # verifying if 'page' works for n8n forum or if it uses 'no_definitions'
            
            resp = requests.get(url, headers=self._headers(), params=params)
            if resp.status_code == 404: 
                break
            resp.raise_for_status()
            
            data = resp.json()
            topic_list = data.get("topic_list", {})
            topics = topic_list.get("topics", [])
            
            if not topics:
                break
                
            for t in topics:
                # Filter for logic/workflow related? Or just everything?
                # The user want "workflow signals". We assume all topics might be relevant or 
                # maybe filter by category if known (e.g. 'Questions', 'Made with n8n').
                # For MVP fetch all latest.
                
                metrics = compute_ratios(
                    views=t.get("views", 0),
                    likes=t.get("like_count", 0), # Discourse often uses 'like_count' or 'actions_summary'
                    comments=t.get("posts_count", 0) - 1 # posts includes OP?
                )
                
                results.append({
                    "platform": "Discourse",
                    "source_id": str(t["id"]),
                    "source_url": f"{self.base_url}/t/{t['slug']}/{t['id']}",
                    "workflow": t["title"],
                    "normalized_title": normalize_title(t["title"]),
                    "country": "Global", # Discourse is global
                    "popularity_metrics": metrics,
                    "collected_at": t.get("created_at")
                })
        
        return results
