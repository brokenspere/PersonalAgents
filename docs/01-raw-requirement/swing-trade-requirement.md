# AI-Powered Stock Screener Flow (MCP & yfinance)

This document outlines the end-to-end architecture and data flow for an AI-driven stock screening system utilizing the Model Context Protocol (MCP) and a Python backend.

---

## 📥 1. INPUT (Data & Triggers)

The starting point that initiates the scanning process. It consists of two main components:

- **Triggers (Initiators):**
  - **Manual Trigger:** A user prompts the AI via a chat interface (e.g., _"Scan for tech stocks in a perfect uptrend"_).
  - **Automated Trigger:** An Event-Driven Scheduler fires an event (e.g., `market.close`) automatically after trading hours.
- **Data Sources:**
  - **Universe / Watchlist:** A predefined list of stock tickers (e.g., AAPL, NVDA, SPY) to scan.
  - **Raw Market Data:** OHLCV (Open, High, Low, Close, Volume) data targeted for retrieval via the Yahoo Finance API.

---

## ⚙️ 2. PROCESS (Execution & Logic)

The collaborative phase between the AI's natural language understanding and the backend's computational power.

- **AI Routing:** The AI Client recognizes it lacks real-time financial data and forwards the user's intent to your custom MCP Server via the **MCP Protocol**.
- **Data Fetching:** The MCP Server receives the request and executes the Python SDK (`yfinance`) to fetch the historical stock data.
- **Calculation:** Python libraries (such as `pandas`) compute the necessary technical indicators (e.g., SMA 20, SMA 50, SMA 200).
- **Logic Filtering:** The computed data is strictly evaluated against predefined trading rules (e.g., filtering out stocks where Price is below SMA 200, ensuring SMAs are perfectly aligned for an uptrend).

---

## 📤 3. OUTPUT (Results & Delivery)

The final phase where the filtered data is transformed into actionable trading setups.

- **Data Return:** The MCP Server sends the filtered, structured data (e.g., a list of matching tickers and their current prices) back to the AI Client.
- **AI Summarization:** The LLM digests the raw data array and generates a human-readable trading plan, outlining precise entry points (Buy Limit), Stop Loss, and Take Profit levels.
- **Final Delivery:**
  - _Direct Output:_ Displayed directly on the user's chat screen.
  - _Notification Output:_ Routed to a Notification Worker to trigger alerts on platforms like Telegram or Discord for immediate execution before going to sleep.
