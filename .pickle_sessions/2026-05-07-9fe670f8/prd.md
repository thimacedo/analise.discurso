# Source Control Verification PRD

## HR Eng

| Source Control Verification PRD |  | This PRD outlines the requirements for a process to verify the source control status, ensuring clean commits and identifying unwanted files in the repository. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick 🥒 **Contributors**: [User] **Intended audience**: Engineering | **Status**: Draft **Created**: 2026-05-07 | **Self Link**: N/A **Context**: User prompt "verifique o source control para ver se algo precisa ser commitado ou se é lixo"

## Introduction

This document defines the requirements for a new process to inspect the Git repository's status. The goal is to ensure that only intended changes are staged and committed, and to identify any extraneous or "junk" files that should not be part of the codebase.

## Problem Statement

**Current Process:** Ad-hoc checks of Git status, potentially leading to overlooked changes, accidental commits, or inclusion of temporary/unnecessary files.
**Primary Users:** Developers working on the Sentinela Democrática project.
**Pain Points:** Lack of a consistent, automated check for repository cleanliness, increasing the risk of introducing bugs or clutter through commits.
**Importance:** To maintain code integrity, facilitate easier collaboration, and reduce the likelihood of regressions caused by incorrect source control management.

## Objective & Scope

**Objective:** To establish a robust and clear process for verifying the source control status before committing.
**Ideal Outcome:** Developers have high confidence that their repository is clean and that only desired changes are being managed by Git.

### In-scope or Goals
- Check for uncommitted changes (modified files).
- Check for staged changes.
- Identify untracked files.
- Provide clear output indicating the repository's state.

### Not-in-scope or Non-Goals
- Automatically committing or reverting changes.
- Deep analysis of file content (beyond identifying untracked files).
- Handling non-Git version control systems.

## Product Requirements

### Critical User Journeys (CUJs)
1.  **Developer checks repository status:**
    a. Developer initiates the source control check.
    b. System reports staged, unstaged, and untracked files.
    c. Developer reviews the output.
2.  **Developer sees untracked files:**
    a. Developer initiates the source control check.
    b. System reports untracked files (potential "lixo").
    c. Developer is alerted to review these files.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | The system must report on modified (unstaged) files. | As a developer, I want to see a list of modified files that have not yet been staged. |
| P0 | The system must report on staged files. | As a developer, I want to see a list of files that are staged for commit. |
| P0 | The system must report on untracked files. | As a developer, I want to see a list of files that are not currently tracked by Git. |
| P1 | The system should provide a summary of the repository's state. | As a developer, I want a quick overview of whether the repository is clean or has pending changes/untracked files. |
| P1 | The system should alert the user to potential "junk" files (untracked files). | As a developer, I want to be alerted to untracked files that might be unintentional. |

## Assumptions

- The project uses Git for source control.
- The user has basic familiarity with Git concepts (staged, unstaged, untracked).

## Risks & Mitigations

- **Risk**: The prompt is too ambiguous to provide a precise check. -> **Mitigation**: Make reasonable inferences for the scope, clearly stating them in the PRD.
- **Risk**: The user expects automated actions (commit/revert). -> **Mitigation**: Explicitly state that this process is for verification only, not automated changes.

## Tradeoff

- **Option Considered**: Implementing a pre-commit hook.
- **Pros**: Automated enforcement.
- **Cons**: Might be too intrusive or complex for initial setup. Requires configuration across environments.
- **Chosen Approach**: A manual check command that provides clear output, allowing the developer to make informed decisions. This is simpler and less intrusive for initial verification.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| Number of commits with accidental/untracked files | Unknown/High | 0 | Reduced technical debt, improved code quality |
| Developer confidence in repository state | Low | High | Faster development cycles, fewer merge conflicts |
