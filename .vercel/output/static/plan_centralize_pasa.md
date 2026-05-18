# Implementation Plan: Centralize PASA Classification Logic

## Goal
Centralize all PASA v16.4 classification rules, prompt engineering, and parsing into a dedicated `ForensicsService` to ensure consistency and enable rigorous audit logging.

## Phase 1: Infrastructure
1.  **Create `core/forensics_service.py`:**
    *   Define `ForensicVerdict` (TypedDict or dataclass) for structured outputs.
    *   Implement `PasaForensicsService` class.
    *   Move `SYSTEM_PROMPT_PASA` to this service and enhance it based on `PADRONIZACAO_LINGUISTICA_FORENSE.md`.
    *   Implement `get_prompt(text: str)` method.
    *   Implement `parse_verdict(raw_response: str)` method.
    *   Implement `log_audit(text, verdict, engine)` for forensic tracing.

## Phase 2: Refactoring `AIService`
1.  **Update `core/ai_service.py`:**
    *   Import `PasaForensicsService`.
    *   Remove `SYSTEM_PROMPT_PASA` and `_parse_response` from `AIEngine` / `AIService`.
    *   Update `AIEngine.classify` to use `PasaForensicsService` for prompt generation and response parsing.
    *   Ensure all engines (Gemini, Groq, Ollama) use the centralized logic.

## Phase 3: Integration and Cleanup
1.  **Update `core/pasa_auditor.py`:**
    *   Ensure it leverages the new `ForensicsService` if necessary (though it mostly uses `AIService`).
2.  **Update `processing/ad_processor.py`:**
    *   Verify it still works correctly with the refactored `AIService`.
3.  **Update `core/orquestrador.py`:**
    *   Check for any direct dependencies on the old logic.

## Phase 4: Verification
1.  **Create `tests/test_forensics_service.py`:**
    *   Test prompt generation.
    *   Test parsing with various AI outputs (clean JSON, markdown-wrapped JSON, malformed JSON).
    *   Test category validation.
2.  **Run manual classification test:**
    *   Use a script to run a classification and check the logs.

## Success Criteria
- [ ] `core/forensics_service.py` exists and contains all PASA logic.
- [ ] `core/ai_service.py` is free of hardcoded prompts and parsing logic.
- [ ] Tests pass for various input scenarios.
- [ ] Audit logs show detailed reasoning for classifications.

---
*Planned by: Pickle Rick 🥒*
