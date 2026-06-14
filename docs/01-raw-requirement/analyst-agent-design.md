# Design Document: Financial Analyst Agent

## 1. Overview

The Financial Analyst Agent is a new, specialized component designed to provide deep, actionable insights on news scraped by the Yahoo Finance agent. It operates within the existing serverless event-driven architecture, triggering via SQS (`analyst_queue`) to perform asynchronous analysis.

## 2. Architectural Role

- **Input:** Triggered by SQS messages containing `EnrichedPayload` (headline data, extracted tickers, and VADER sentiment).
- **Data Augmentation:** Uses `yfinance` to fetch basic technical and fundamental data for the extracted tickers to ground the LLM and prevent hallucination.
- **Processing:** Utilizes the Google Gemini API for deep financial analysis, evaluating news impact, identifying market trends, and synthesizing insights.
- **Output:** Publishes an `AnalyzedPayload` to the `notification_queue` for delivery.
- **Decoupling:** Operates independently of the Scraper, Enrichment, and Notification workers.

## 3. Workflow

1. **Event Consumption:** The AWS Lambda handler picks up an SQS message from `analyst_queue` containing the batched `EnrichedPayload`.
2. **Data Augmentation:** Fetches historical/fundamental data for each ticker using `yfinance`.
3. **Analysis Execution:**
   - Pre-processes news data alongside the fetched market data.
   - Queries the Gemini API for structured analysis (Impact assessment, trend identification, summary).
4. **Payload Construction:** Creates a batched `AnalyzedPayload` containing a list of `AnalyzedHeadlineItem`s with derived insights and impact scores.
5. **Event Publication:** Pushes the payload to the `notification_queue` via SQS.

## 4. Proposed Data Schema (`shared/models.py`)

```python
class AnalyzedHeadlineItem(EnrichedHeadlineItem):
    insights: str
    impact_score: float # -1.0 to 1.0

class AnalyzedPayload(BaseModel):
    source: str
    market: Optional[str]
    timestamp: datetime
    items: List[AnalyzedHeadlineItem]
    trending_tickers: List[str]
```

## 5. Technical Requirements

- **LLM Integration:** Secure integration with the Google Generative AI Python SDK.
- **Market Data:** Utilize the `yfinance` library for data fetching.
- **Security:** The Gemini API key must be managed via AWS SSM Parameter Store and injected into the Lambda environment variables via Terraform.
- **Execution:** AWS Lambda function triggered by SQS.

## 6. Implementation Steps

1. **Model Definition:** Extend `shared/models.py` to include `AnalyzedPayload` and `AnalyzedHeadlineItem`.
2. **Infrastructure:** Update Terraform to provision `analyst_queue` SQS, SSM Parameter Store for `GEMINI_API_KEY`, and the Analyst Agent Lambda.
3. **Agent Logic:** Create `workers/analyst/handlers.py` and `service.py`. Develop `yfinance` integration and Gemini API prompt engineering.
4. **Pipeline Integration:** Update EnrichmentWorker to output to `analyst_queue` instead of `notification_queue`.

## 7. Agent System Prompt

```
You are a sophisticated financial analysis agent. You are provided with a news headline, its VADER sentiment score, and recently fetched technical/fundamental data for the associated tickers.
Your task is to analyze this data and provide insightful recommendations. Evaluate the potential impact of the news in the context of the current market data. Be balanced in your analysis, highlighting both potential risks and opportunities. Provide a clear impact score between -1.0 and 1.0, along with a concise summary of insights.

CRITICAL INSTRUCTION: You must provide your final summary and all recommendations entirely in the Thai language.
```