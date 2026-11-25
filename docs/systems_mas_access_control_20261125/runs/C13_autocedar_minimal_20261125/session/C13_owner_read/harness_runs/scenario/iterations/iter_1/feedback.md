## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** unexpected token `principal`
  Example (first occurrence):
  ```
  ╭─[2:5]
 1 │ permit(principal, action == readDocument, resource) when
 2 │     principal is User
   ·     ────┬────
   ·         ╰── expected `{`
 3 │     && resource is Document
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.