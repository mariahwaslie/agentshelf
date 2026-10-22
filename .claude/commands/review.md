---
description: Independent code review of this session's changes by the reviewer agent
---
Use the **reviewer** subagent to review the changes since the last `prompt-*-done` tag (or the whole repo if the prompt asks for a full review).

Give the reviewer: the current prompt file path, `git diff <last-tag>..HEAD --stat`, and the list of changed files. Do not summarize your own intent to it — it should judge the code as it is.

When it returns, list its findings in a table (finding, severity, file:line). Fix every **High** and **Medium** finding, re-run `make check`, and record all findings (fixed or deferred with reason) in the Verification Report.
