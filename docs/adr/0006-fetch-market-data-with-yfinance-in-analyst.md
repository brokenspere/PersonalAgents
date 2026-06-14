# Fetch Market Data with yfinance in Analyst Agent

## Context

The Analyst Agent needs to analyze financial news and provide insights (e.g., impact scores). The system prompt originally requested the LLM to consider technical indicators and fundamental analysis. However, the input to the agent (`EnrichedPayload`) only provides the news headline, URL, sentiment score, and extracted tickers. Without actual market data, the LLM is highly likely to hallucinate technical and fundamental analysis.

## Decision

We decided to integrate the `yfinance` library directly within the Analyst Agent Lambda function. Before calling the Gemini LLM, the agent will use `yfinance` to fetch basic technical and fundamental data for the tickers associated with the news item. The LLM prompt will then be augmented with this real data.

## Consequences

- **Easier:** Prevents LLM hallucination and grounds the analysis in real market data.
- **More difficult:** Adds a heavy dependency (`yfinance`) to the Lambda deployment package, potentially increasing cold start times and deployment size. It also adds runtime latency for the external API calls to Yahoo Finance.