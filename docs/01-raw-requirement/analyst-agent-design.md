# Design Document: Financial Analyst Agent

## 1. Overview
The Financial Analyst Agent is a new, specialized component designed to provide deep, actionable insights on news scraped by the Yahoo Finance agent. It operates within the existing event-driven architecture, subscribing to the `news.ready` event queue to perform asynchronous analysis.

## 2. Architectural Role
- **Input:** Subscribes to `news.ready` events (containing headline data, tickers, and sentiment).
- **Processing:** Utilizes the Google Gemini API for deep financial analysis, evaluating news impact, identifying market trends, and synthesizing insights.
- **Output:** Publishes an `analysis.ready` event containing the processed insights.
- **Decoupling:** Operates independently of the Scraper and Notification services.

## 3. Workflow
1. **Event Consumption:** The agent picks up a `news.ready` payload from the message broker.
2. **Analysis Execution:**
   - Pre-processes news data.
   - Queries the Gemini API for structured analysis (Impact assessment, trend identification, summary).
3. **Payload Construction:** Creates an `AnalysisPayload` containing the original item, the derived insights, and metadata.
4. **Event Publication:** Pushes `analysis.ready` to the broker.

## 4. Proposed Data Schema (`shared/models.py`)

```python
class AnalysisPayload(BaseModel):
    original_item: HeadlineItem
    insights: str
    impact_score: float # -1.0 to 1.0
    tickers: List[str]
```

## 5. Technical Requirements
- **LLM Integration:** Secure integration with the Google Generative AI Python SDK.
- **Security:** API keys must be managed via environment variables (`GEMINI_API_KEY`) and never committed to version control.
- **Async Execution:** Must implement Celery worker tasks to ensure non-blocking operation.
- **Resource Management:** Independent container (e.g., `workers/analyst/Dockerfile`) to allow for specific hardware requirements if needed.

## 6. Implementation Steps
1. **Model Definition:** Extend `shared/models.py` to include `AnalysisPayload`.
2. **Agent Skeleton:** Create `workers/analyst/` with `service.py`, `tasks.py`, and `Dockerfile`.
3. **Logic Implementation:** Develop Gemini API integration, prompt engineering, and analysis logic using the official SDK.
4. **Broker Integration:** Configure the agent to subscribe to `news.ready` and publish to `analysis.ready`.
5. **Notification Update:** Update the notification worker to consume and dispatch `analysis.ready` events.
