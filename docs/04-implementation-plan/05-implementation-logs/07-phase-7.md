# Phase 7: Screener Agent Implementation

## Status
**Completed**

## Overview
This phase focused on implementing the post-market Swing Trade Screener Agent. The ScreenerAgent is a systematic trading agent that filters a predefined watchlist of tickers based on strict technical criteria (Moving Average Pullback strategy) and generates a swing trading plan using the LLM.

## Implementation Details

1. **Data Models Extension:**
   - Appended `ScreenedTickerItem` and `ScreenedPayload` to `shared/models.py`.
   - Included technical metrics (SMA 20, 50, 200), current price, upcoming earnings date, and macro event risk flag.

2. **Terraform Infrastructure:**
   - **`lambda.tf`:** Provisioned the `screener_function` Lambda resource.
   - **`iam.tf`:** Created `screener_lambda_role`, `screener_sqs_policy` (to publish to the `notification_queue`), and `screener_ssm_policy` (to read the `GEMINI_API_KEY_SSM`).
   - **`eventbridge.tf`:** Set up the EventBridge target and permission to directly invoke the `screener_function` on the `market.close` event.

3. **Screener Worker Implementation (`workers/screener/`):**
   - **`service.py`:** 
     - Predefined a high-liquidity watchlist (`AAPL`, `MSFT`, `GOOGL`, etc.).
     - Implemented `check_macro_event_risk()` reading from `shared/economic_calendar.json` for high-impact events within 7 days.
     - Fetched historical data using `yfinance` and extracted upcoming earnings dates.
     - Calculated technical indicators (SMA 20, 50, 200) utilizing `pandas`.
     - Executed strict technical filtering for perfect uptrend (`SMA 20 > SMA 50 > SMA 200` and `Current Price > SMA 200`).
     - Integrated the Google Gemini API to analyze passing tickers and output an actionable trading plan in Thai, governed by `.gemini/agents/swing-trade-assistant.md`.
   - **`handlers.py`:** 
     - Created `eventbridge_handler` to intercept `market.close` events, fetch the SSM parameter, execute the screener logic, and publish the `ScreenedPayload` to the SQS `notification_queue`.

4. **Notification Integration:**
   - Modified `workers/notification/handlers.py` to differentiate between `AnalyzedPayload` and `ScreenedPayload`.
   - Updated `workers/notification/service.py` with `format_screened_payload_telegram` to securely formulate HTML notifications tailored for the screener report and LLM-generated trading plan.

5. **Testing:**
   - Created `tests/test_screener.py` utilizing `unittest.mock` to validate the technical filtering process and payload construction against mocked `yfinance` output.
