## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** `startsWith` is not a valid method
  Example (first occurrence):
  ```
  ╭─[6:8]
 5 │     && resource.approvalCount >= 1
 6 │     && resource.targetBranch.startsWith("hotfix/")
   ·        ───────────────────────────────────────────
 7 │ };
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.