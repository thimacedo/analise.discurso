# Research Review: PASA v16.4 Classification Centralization

## Current State
- **Logic Spread:** PASA v16.4 classification logic is primarily located in `core/ai_service.py` (within `SYSTEM_PROMPT_PASA` and `AIEngine._parse_response`).
- **Usage:** Used by `AIService.classify`, which is called by `PASAAuditor.process` and `AdProcessor.process_item_batch`.
- **Inconsistencies:** The categories in `ai_service.py` (v16.4) and `docs/PADRONIZACAO_LINGUISTICA_FORENSE.md` (v16.3) differ slightly.
- **Audit Logging:** Currently limited. The "reason" is captured but not rigorously logged as a forensic "trace".
- **Terminology:** `PASAAuditor` handles basic terminology replacement (e.g., "laudo" -> "dossiê") which is part of the PASA protocol to avoid legal friction.

## Key Files Identified
- `core/ai_service.py`: Contains the prompt and the AI orchestration logic.
- `core/pasa_auditor.py`: Handles terminology audit.
- `processing/ad_processor.py`: Processes Meta ads using the classification.
- `docs/PADRONIZACAO_LINGUISTICA_FORENSE.md`: Theoretical basis for classification.
- `docs/OPERACAO_TECNICA_v16_4.md`: Operational flow.

## Requirements for Centralization
1. **Dedicated Module:** Create `core/forensics_service.py`.
2. **Standardized Prompt:** Consolidate categories and rules into a single, versioned prompt generator.
3. **Robust Parsing:** Centralize JSON parsing and validation of AI responses.
4. **Forensic Trace:** Implement a structured way to capture "why" a classification was made (evidence, reasoning, confidence).
5. **Consistency:** Ensure all content types (comments, ads, etc.) use the same classification engine.

## Proposed Architecture
- `PasaForensicsService`: The main class for PASA operations.
- `ForensicVerdict`: A data class/model for structured output.
- `AuditLog`: A mechanism to record every classification event with its full trace.

---
*Reviewed by: Pickle Rick 🥒*
