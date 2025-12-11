CREATE TABLE workflows (
  id BIGSERIAL PRIMARY KEY,
  platform VARCHAR(32) NOT NULL,
  source_id TEXT,
  source_url TEXT,
  workflow TEXT NOT NULL,
  normalized_title TEXT,
  country VARCHAR(32),
  popularity_metrics JSONB NOT NULL,
  latest_metrics JSONB,
  score NUMERIC DEFAULT 0,
  first_seen TIMESTAMP WITH TIME ZONE DEFAULT now(),
  last_seen TIMESTAMP WITH TIME ZONE DEFAULT now(),
  inserted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  raw_snapshots JSONB[],
  UNIQUE (platform, source_id)
);

CREATE INDEX idx_platform_country ON workflows (platform, country);
CREATE INDEX idx_score ON workflows (score DESC);
CREATE INDEX idx_normalized_title_gin ON workflows USING gin (to_tsvector('english', normalized_title));
