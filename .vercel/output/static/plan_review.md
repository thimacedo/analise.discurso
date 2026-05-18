# Plan Review: Centralize PASA Classification Logic

## Architectural Soundness
- **Decoupling:** Moving PASA logic to `ForensicsService` correctly decouples the *domain rules* (PASA) from the *infrastructure* (AI Engines/Cascading).
- **Consistency:** Centralizing the prompt ensures that all AI engines (Gemini, Groq, Ollama) receive the exact same instructions and their outputs are parsed identically.
- **Maintainability:** Future changes to PASA v16.5 or categories will only need to be updated in one file.

## Specificity
- The plan identifies the exact files to be modified and the new components to be created.
- It specifies the methods to be implemented in the new service.

## Safety and Risks
- **Risk:** Breaking the classification pipeline if the refactoring is incomplete.
- **Mitigation:** The plan includes a verification phase with specific tests and a manual check.
- **Risk:** Data loss during migration of logic.
- **Mitigation:** Logic is being *moved* and *refined*, not deleted. Git history is available.

## Missing Details
- Need to decide on the final set of categories for v16.4. I will merge the ones from `ai_service.py` with the theoretical ones from the docs if they add value, but will prioritize `ai_service.py` as the current "hot" implementation.

---
*Reviewed by: Pickle Rick 🥒*
