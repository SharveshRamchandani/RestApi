import os
import backoff
from opensearchpy import OpenSearch, RequestsHttpConnection

host = os.getenv("OPENSEARCH_HOST", "localhost")
port = int(os.getenv("OPENSEARCH_PORT", 9200))
auth = (os.getenv("OPENSEARCH_USER", "admin"), os.getenv("OPENSEARCH_PASSWORD", "admin"))

# Initialize client
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=auth,
    use_ssl=False,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)

INDEX_NAME = "n8n_workflows"

def create_index():
    if not client.indices.exists(index=INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body={
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            },
            "mappings": {
                "properties": {
                    "workflow": {"type": "text"},
                    "description": {"type": "text"},
                    "platform": {"type": "keyword"},
                    "score": {"type": "float"},
                    "country": {"type": "keyword"}
                }
            }
        })

@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def index_item(item: dict):
    # Doc ID is platform + source_id
    doc_id = f"{item['platform']}-{item['source_id']}"
    
    doc = {
        "workflow": item["workflow"],
        "normalized_title": item.get("normalized_title"),
        "platform": item["platform"],
        "country": item.get("country"),
        "score": item.get("popularity_metrics", {}).get("views", 0), # Simplified score
        "last_seen": item.get("collected_at")
    }
    
    client.index(
        index=INDEX_NAME,
        body=doc,
        id=doc_id,
        refresh=True
    )
