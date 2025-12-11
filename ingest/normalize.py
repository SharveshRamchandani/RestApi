import re

def normalize_title(title: str) -> str:
    if not title:
        return ""
    t = title.strip().lower()
    t = re.sub(r'\s+', ' ', t)
    # Remove durations like 12:34
    t = re.sub(r'\d{1,2}:\d{2}', '', t)
    return t.strip()

def compute_ratios(views, likes, comments):
    views = int(views) if views else 0
    likes = int(likes) if likes else 0
    comments = int(comments) if comments else 0
    
    return {
       "views": views,
       "likes": likes,
       "comments": comments,
       "like_to_view_ratio": round(likes / views, 6) if views else 0,
       "comment_to_view_ratio": round(comments / views, 6) if views else 0
    }
