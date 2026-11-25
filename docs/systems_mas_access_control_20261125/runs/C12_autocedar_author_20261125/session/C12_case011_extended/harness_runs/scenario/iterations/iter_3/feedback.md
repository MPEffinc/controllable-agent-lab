## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** `size` is not a valid method
  Example (first occurrence):
  ```
  ╭─[6:8]
 5 │     && resource.approvalCount >= 1
 6 │     && resource.targetBranch.size() >= 7
   ·        ────────────────────────────
 7 │     && resource.targetBranch.substr(0,7) == "hotfix/"
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.

**Error:** `substr` is not a valid method
  Example (first occurrence):
  ```
  ╭─[7:8]
 6 │     && resource.targetBranch.size() >= 7
 7 │     && resource.targetBranch.substr(0,7) == "hotfix/"
   ·        ─────────────────────────────────
 8 │ };
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.