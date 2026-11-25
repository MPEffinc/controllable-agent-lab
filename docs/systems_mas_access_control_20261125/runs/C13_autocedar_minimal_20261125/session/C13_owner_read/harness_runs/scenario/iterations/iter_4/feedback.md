## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** unexpected token `{`
  Example (first occurrence):
  ```
  ╭─[1:37]
 1 │ permit(principal, action, resource) {
   ·                                     ┬
   ·                                     ╰── expected `;` or identifier
 2 │   principal is User
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.