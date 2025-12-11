from ingest.normalize import normalize_title, compute_ratios

def test_normalize_title():
    assert normalize_title("  Test  Title 12:34 ") == "test title"
    assert normalize_title("n8n workflow") == "n8n workflow"
    assert normalize_title("") == ""

def test_compute_ratios():
    metrics = compute_ratios(100, 10, 5)
    assert metrics["views"] == 100
    assert metrics["like_to_view_ratio"] == 0.1
    assert metrics["comment_to_view_ratio"] == 0.05
    
    # Zero division check
    metrics_zero = compute_ratios(0, 0, 0)
    assert metrics_zero["like_to_view_ratio"] == 0
