# Epic Refactor: Processing Architecture v2.0

## HR Eng

| Epic Refactor: Processing Architecture v2.0 |  | [Refactoring the core data processing pipeline to improve scalability, reliability, and forensic integrity of the Sentinela Democratica platform.] |
| :---- | :---- | :---- |
| **Author**: Pickle Rick **Contributors**: Gemini CLI **Intended audience**: Engineering, PM | **Status**: Draft **Created**: 2026-05-06 | **Self Link**: [Local] **Context**: [Sentinela Project] 

## Introduction

The current processing architecture of Sentinela Democratica consists of fragmented components (`ad_processor.py`, `data_miner.py`, `text_processor.py`, etc.) that lack a unified execution model. This refactor aims to consolidate these into a robust, event-driven, or batch-oriented pipeline that ensures every piece of collected data is rigorously audited according to the PASA v16.4 protocol.

## Problem Statement

**Current Process:** Processing is triggered manually or via basic loops that pull from the database. Each processor handles its own logic, error handling, and DB interactions.
**Primary Users:** Backend Engineers, Forensic Analysts.
**Pain Points:** 
- **Inconsistency:** Different processors handle metadata and classification differently.
- **Scalability:** Hard to scale horizontally without duplicate processing risks.
- **Resilience:** If one processing step fails, it's hard to resume without reprocessing everything.
- **Slop:** Existing code has boilerplate and lacks a clear "Worker" abstraction.
**Importance:** As we scale to thousands of ads and comments per hour for the 2026 elections, the current system will choke. We need "God Mode" efficiency.

## Objective & Scope

**Objective:** Consolidate all processing logic into a unified `CoreProcessor` or `Worker` system.
**Ideal Outcome:** A single entry point for processing any data type (Ad, Comment, Post) with automated retry logic, unified logging, and 100% PASA compliance.

### In-scope or Goals
- Create a `BaseWorker` abstraction for all processing tasks.
- Implement a `Queue-based` or `Poll-based` orchestration system.
- Refactor `ad_processor.py` and `data_miner.py` to use the new architecture.
- Centralize PASA classification logic.
- Optimize database interactions (batch updates).

### Not-in-scope or Non-Goals
- Changing the Scraping logic (Scrapers remain as is for now).
- Frontend changes (Dashboard remains unchanged, just receives better data).
- Replacing Supabase (We stay on the current DB).

## Product Requirements

### Critical User Journeys (CUJs)
1. **Unified Processing**: When a scraper dumps raw data into the DB, the `ProcessingWorker` picks it up, runs cleaning, PASA classification, and thematic clustering in a single transactional flow.
2. **Error Recovery**: If an IA provider fails, the worker marks the item for "Retry" and backs off, preventing data loss or partial processing.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Unified Worker Abstraction | As a developer, I want a base class to handle processing boilerplate so I only write logic. |
| P0 | Batch Database Operations | As a system, I want to update multiple records at once to save IO and API costs. |
| P1 | Forensic Audit Logging | As an analyst, I want a log of WHY a piece of content was classified as it was (PASA trace). |
| P1 | Performance Monitoring | As an engineer, I want to know the processing latency per item. |
| P2 | Dynamic Clustering | As an analyst, I want thematic clusters to update automatically as new data arrives. |

## Assumptions

- The Supabase connection is stable and can handle batch operations.
- The `AIService` (local or Gemini) has sufficient throughput.

## Risks & Mitigations

- **Risk**: Refactoring might break existing classification logic. -> **Mitigation**: Implement unit tests for PASA classification before and after refactor.
- **Risk**: Batch updates might exceed Supabase/PostgreSQL limits. -> **Mitigation**: Use controlled chunking (e.g., 100 records per batch).

## Tradeoff

- **Option Considered**: Moving to a dedicated Queue (RabbitMQ/Redis).
- **Decision**: Stay with DB-polling for now to minimize infrastructure complexity, but design the architecture to be "Queue-ready".

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| Processing Throughput | ~10 items/sec | >100 items/sec | 10x scalability |
| Error Rate | Unmonitored | < 1% | Higher data reliability |
| Dev Speed (New Processor) | 2-3 hours | < 30 mins | Faster feature delivery |

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| Pickle Rick | Engineering | God Emperor | Refactor Lead |
| Forensic Team | Analysts | Consumers | Accuracy Verification |
