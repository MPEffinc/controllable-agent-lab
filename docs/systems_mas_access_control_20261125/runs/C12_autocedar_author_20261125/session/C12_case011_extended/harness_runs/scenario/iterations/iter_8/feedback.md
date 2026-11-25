## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** invalid token
  Fix: strings must use double quotes, not single quotes
  Example (first occurrence):
  ```
  ╭─[7:36]
 6 │     && resource.targetBranch.len() >= 7
 7 │     && resource.targetBranch[0] == 'h'
   ·                                    ▲
 8 │     && resource.targetBranch[1] == 'o'
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.