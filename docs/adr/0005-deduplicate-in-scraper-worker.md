# Deduplicate Headlines in Scraper Worker

To prevent redundant notifications within a 24-hour window, we need a Redis-based caching mechanism. We decided to place this deduplication logic early in the pipeline, specifically within the ScraperWorker, before the `ExtractionPayload` is published to the message broker. 

This prevents duplicate data from flowing downstream, significantly saving compute resources and latency that would otherwise be wasted on redundant natural language processing (sentiment analysis and ticker extraction) in the Enrichment Worker.
