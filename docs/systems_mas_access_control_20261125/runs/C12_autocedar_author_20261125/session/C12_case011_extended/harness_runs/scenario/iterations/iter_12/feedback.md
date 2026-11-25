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