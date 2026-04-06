# Command Execution Contract

Standards for SDD workflow command structure and execution.

## 1) Map-First Structure
- Start with Purpose, Required Inputs, Expected Outputs before detailed steps.
- Keep phase ordering explicit and stable.
- State stop conditions and failure exits before dependent phases.

## 2) Agent Legibility
- Prefer short imperative steps over narrative paragraphs.
- Keep one rule in one place. Reuse shared references for repeated blocks.
- Make each phase independently understandable with minimal backtracking.

## 3) Size Discipline
- Recommended command size target: <= 180 lines per command file.
- If a command exceeds target, keep behavior but annotate why and point to extraction candidates.

## 4) Feedback Loop
- If the same review issue repeats across runs, update source command text (not only output docs).
- Keep canonical source in commands/; mirrors must remain source-identical.

## 5) Input/Output Contracts per Delegation
- Before each subagent call, list required inputs explicitly.
- After each subagent call, list expected outputs and validation gate to proceed.
