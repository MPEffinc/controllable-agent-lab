## Verification Results — 1 check(s) FAILED

**🛑 STOP — REPEATED POLICY DETECTED 🛑**
You just submitted a byte-identical policy to the one you submitted at iteration 6. You are in a loop.

Across all your recent attempts, the following failure modes have appeared (sometimes alternating between iterations):
  - syntax

**Every single one of these must be fixed AT THE SAME TIME, in ONE policy.** You cannot fix one by trading off another. Do not remove a guard (`has`, `==`, role check) to satisfy a different check — that just sends the previous failure back. Reason about the conjunction of constraints, not one at a time.

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