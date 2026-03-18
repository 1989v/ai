---
name: curl-gen
description: "Generate an executable curl command from a natural-language API request"
---

# /curl-gen

Use the `ai-debugger:curl-gen` skill to handle this request.

Follow that skill exactly:
- identify the target API from the user's description and the codebase
- collect only the missing parameters required to produce a valid request
- generate a runnable curl command
- explain any assumptions that were necessary
