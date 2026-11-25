## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** unexpected token `resource`
  Example (first occurrence):
  ```
  ╭─[2:8]
 1 │ permit(principal: User, action == readDocument, resource: Document)
 2 │   when resource.owner == principal;
   ·        ────┬───
   ·            ╰── expected `{`
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.