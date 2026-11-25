## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** unexpected token `{`
  Example (first occurrence):
  ```
  ╭─[1:69]
 1 │ permit(principal: User, action == readDocument, resource: Document) {
   ·                                                                     ┬
   ·                                                                     ╰── expected `;` or identifier
 2 │     resource.owner == principal
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.