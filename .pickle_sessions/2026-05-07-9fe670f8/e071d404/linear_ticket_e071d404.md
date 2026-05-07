---
id: e071d404
title: Implement Check for Uncommitted Changes
status: Todo
priority: High
order: 10
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
Developers need to be aware of modified files that have not yet been staged for commit.

## Solution
Implement a check that identifies and reports any modified files that are not staged. This will typically involve using `git status` and parsing its output.

## Implementation Details
- This ticket will involve writing code that executes a Git command.
- The output of the command needs to be parsed to identify modified, unstaged files.
- The identified files should be reported clearly.
