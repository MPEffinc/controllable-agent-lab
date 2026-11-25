## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** expected an entity uid, found name `readDocument`
  Fix: try including an identifier string if you intended this name to be an
  Example (first occurrence):
  ```
  ╭────
 1 │ permit(principal, action == readDocument, resource) when { resource.owner == principal };
   ·                             ────────────
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.