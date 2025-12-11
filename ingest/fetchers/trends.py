import os
from typing import List, Dict, Any
from pytrends.request import TrendReq
from ingest.normalize import normalize_title

class TrendsFetcher:
    def __init__(self, hl='en-US', tz=360):
        self.pytrends = TrendReq(hl=hl, tz=tz)

    def fetch_trends(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        if not keywords:
            keywords = ["n8n workflow", "n8n automation", "n8n tutorial"]
            
        # Pytrends can be flaky due to Google internal API changes/rate limits.
        # We wrap in try/except or just allow failure.
        results = []
        
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')
            data = self.pytrends.interest_over_time()
            
            if data.empty:
                return []
                
            # Convert trend data to "workflow" signals? 
            # The prompt asks for "signals... upserts canonical workflow records".
            # Keyword trends don't map 1:1 to a specific "workflow" entity like a video or forum topic.
            # They map to the keyword itself.
            # We will treat the KEYWORD as the "workflow" name/title.
            
            # Average interest over the period
            means = data.mean()
            
            for kw in keywords:
                if kw in means:
                    score = float(means[kw])
                    # Synthetic metrics for trends
                    metrics = {
                        "views": int(score * 100), # arbitrary scaling
                        "likes": 0,
                        "comments": 0,
                        "trend_score": score
                    }
                    
                    results.append({
                        "platform": "GoogleTrends",
                        "source_id": f"kw-{kw}",
                        "source_url": f"https://trends.google.com/trends/explore?q={kw}",
                        "workflow": kw, # The keyword is the entity
                        "normalized_title": normalize_title(kw),
                        "country": "Global",
                        "popularity_metrics": metrics,
                        "collected_at": None # now
                    })
                    
        except Exception as e:
            print(f"Error fetching trends: {e}")
            
        return results
