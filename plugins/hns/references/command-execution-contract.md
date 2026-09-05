# Command Execution Contract

Standards for hns skill structure and execution (skills/<name>/SKILL.md).

## 1) Map-First Structure
- Start with Purpose, Required Inputs, Expected Outputs before detailed steps.
- Keep phase ordering explicit and stable.
- State stop conditions and failure exits before dependent phases.

## 2) Agent Legibility
- Prefer short imperative steps over narrative paragraphs.
- Keep one rule in one place. Reuse shared references for repeated blocks.
- Make each phase independently understandable with minimal backtracking.

## 3) Size Discipline
- Recommended size: <= 180 lines per SKILL.md. Heavy reference goes to a supporting file in the same folder.
- The skill body stays in context for the rest of the session once invoked — every line is a recurring cost.

## 4) Feedback Loop
- If the same review issue repeats across runs, update source command text (not only output docs).
- Keep canonical source in skills/; a skill name is its directory name (frontmatter `name` does not override it).

## 5) Input/Output Contracts per Delegation
- Before each subagent call, list required inputs explicitly.
- After each subagent call, list expected outputs and validation gate to proceed.
