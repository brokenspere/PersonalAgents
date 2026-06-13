# Requirements Addendum: Scraper Feature Enhancements

## 1. Overview
This document outlines the proposed enhancements to the existing Yahoo Finance scraper agent. The goal is to evolve the agent from a simple headline aggregator into a financial intelligence tool capable of providing actionable, context-rich data.

## 2. Proposed Features

### 2.1. Market Data Contextualization
- **Ticker Entity Extraction:** Implement NLP/regex-based logic to identify stock tickers (e.g., AAPL, TSLA) referenced within headlines.
- **Trending Ticker Scraper:** Extend the scraper to target "Trending Tickers" or "Market Movers" sections on the Yahoo Finance homepage.

### 2.2. Intelligent Sentiment Analysis
- **Headline Sentiment Scoring:** Integrate a sentiment analysis library (e.g., VADER) to assign scores (-1.0 to 1.0) to extracted headlines.
- **Contextual Filtering:** Enhance the notification worker to support alert filtering based on ticker presence and sentiment thresholds.

### 2.3. Time-Series Tracking & Optimization
- **Duplicate Prevention:** Implement a caching mechanism (e.g., Redis) to store headlines and prevent redundant notifications within a 24-hour window.
- **Robustness:** Introduce header rotation and basic circuit breaker patterns to improve network resilience against site blocking.

## 3. Impact on Architecture
- **Data Model Updates:** The `HeadlineItem` model in `shared/models.py` will need to be extended to include `tickers`, `sentiment_score`, and `timestamp`.
- **Pipeline Processing:** A new processing step will be inserted between scraping and notification dispatch to perform ticker identification and sentiment analysis.
- **Resource Allocation:** Increased CPU requirements for NLP/sentiment tasks should be considered when containerizing the enhanced scraper.

## 4. Implementation Priorities
1. **Infrastructure Prep:** Setup Redis for deduplication.
2. **Core Enrichment:** Implement ticker extraction and sentiment scoring logic.
3. **Model Migration:** Update data models and notification payload structure.
4. **Resilience:** Add proxy/header rotation.
