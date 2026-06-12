# Product Requirements Document (PRD): Scalable AI Agent Platform

## 1. Project Overview

**Goal:** Build a highly scalable, event-driven platform capable of hosting and orchestrating multiple specialized AI agents.
**Initial Scope (V1):** Implement the foundational architecture and deploy the first agent: a market news scraper that fetches Yahoo Finance headlines at market open and close, delivering them to designated messaging channels.

## 2. Core Requirements (V1 Features)

- **Time-Based Triggers:** The system must trigger specific events aligned with market hours (e.g., NYSE market open and market close).
- **Data Extraction:** A dedicated agent must scrape top headlines and corresponding hyperlinks from Yahoo Finance.
- **Notification Dispatch:** Scraped data must be formatted and dispatched autonomously to designated Telegram groups/users and Discord channels.
- **Fault Tolerance:** If a notification service (like Discord) goes down, the scraped data should not be lost.

## 3. Architecture Design

To ensure scalability and prevent bottlenecks, the system will use a decoupled, **Event-Driven Microservices Architecture**.

### 3.1. System Flow

1. **Scheduler:** Fires a `market.open` or `market.close` event.
2. **Message Broker:** Receives the event and routes it to subscribed agents.
3. **Scraper Agent:** Receives the trigger, scrapes the data, and publishes a `news.ready` event back to the broker.
4. **Notification Service:** Listens for `news.ready` events and pushes the payload to external APIs.

### 3.2. Tech Stack Recommendations

- **Orchestrator/Scheduler:** Celery Beat, APScheduler, or native CRON.
- **Message Broker:** Redis (recommended for V1) or RabbitMQ/Kafka.
- **Agent Logic:** Python (BeautifulSoup/Playwright for scraping).
- **Infrastructure:** Docker and Docker Compose for containerization.

## 4. Scalability & Future-Proofing Requirements

The platform must be designed so that adding "Agent N" requires zero modifications to "Agent 1".

- **Decoupling:** Agents must not communicate directly with each other or external output APIs. All communication goes through the Message Broker.
- **Event Subscriptions:** Future agents (e.g., an AI Sentiment Analyzer) will simply subscribe to existing queues (like `news.ready`) to perform secondary processing.
- **Independent Resources:** Each agent must be containerized independently so compute resources can be allocated based on the agent's specific needs (e.g., heavy CPU for LLMs, low CPU for simple scrapers).

## 5. Implementation Phases

### Phase 1: Foundation & Delivery

1. **Repository Setup:** Establish a monorepo structure separating configurations, the scheduler, shared broker utilities, and individual agent folders.
2. **Build Notification Service:** Create a standalone worker that listens to a `notifications` queue and executes POST requests to Telegram Bot APIs and Discord Webhooks.

### Phase 2: Agent Development

1. **Build Yahoo Finance Scraper:** Develop the scraping script to extract headlines.
2. **Integrate Message Broker:** Wrap the scraping script into a worker that triggers on `market.*` events and outputs to the `notifications` queue.

### Phase 3: Deployment

1. **Containerization:** Write `Dockerfile`s for the Scheduler, Notification Service, and Scraper Agent.
2. **Orchestration:** Use `docker-compose.yml` to network the local Redis instance and all worker containers together for testing and deployment.
