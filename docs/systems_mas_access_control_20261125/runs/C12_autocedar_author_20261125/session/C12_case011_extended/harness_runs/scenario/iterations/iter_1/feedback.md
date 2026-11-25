## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** expected an entity uid, found name `mergePullRequest`
  Fix: try including an identifier string if you intended this name to be an
  Example (first occurrence):
  ```
  ╭─[1:29]
 1 │ permit(principal, action == mergePullRequest, resource) when {
   ·                             ────────────────
 2 │     principal.roles.contains("Maintainer")
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.

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