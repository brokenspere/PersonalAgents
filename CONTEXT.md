# Scalable Agent Platform

The foundational architecture and shared definitions for an event-driven platform hosting specialized workers and AI agents.

## Language

**Event**:
A JSON payload routed through the message broker, containing at minimum an ISO-8601 timestamp and context-specific identifiers (e.g., {"market": "NYSE"}).
_Avoid_: Message, Trigger

**Extraction Payload**:
Raw, unformatted structured data (e.g., an array of headline/URL objects) published by a Worker, completely agnostic of its final presentation or delivery mechanism.
_Avoid_: Formatted message, Rendered text

**Worker**:
A component that consumes from or publishes to the message broker (e.g., ScraperWorker, NotificationWorker) to perform specialized tasks.
_Avoid_: Service

**Agent**:
A specialized Worker that employs an LLM or autonomous decision-making logic.
_Avoid_: Worker (when referring specifically to AI-driven nodes), Service
