## Verification Results — 1 check(s) FAILED

- syntax (syntax): **FAIL**
  **SYNTAX / PARSE ERROR — your policy failed to parse.**
  No semantic checks can run until syntax is valid.
  Fix the parse errors below, then resubmit.

**Error:** invalid string literal: 0
  Example (first occurrence):
  ```
  ╭─[6:30]
 5 │     && resource.approvalCount >= 1
 6 │     && resource.targetBranch[0] == "h"
   ·                              ─
 7 │     && resource.targetBranch[1] == "o"
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.

**Error:** invalid string literal: 1
  Example (first occurrence):
  ```
  ╭─[7:30]
 6 │     && resource.targetBranch[0] == "h"
 7 │     && resource.targetBranch[1] == "o"
   ·                              ─
 8 │     && resource.targetBranch[2] == "t"
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.

**Error:** invalid string literal: 2
  Example (first occurrence):
  ```
  ╭─[8:30]
 7 │     && resource.targetBranch[1] == "o"
 8 │     && resource.targetBranch[2] == "t"
   ·                              ─
 9 │     && resource.targetBranch[3] == "f"
   ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.

**Error:** invalid string literal: 3
  Example (first occurrence):
  ```
  ╭─[9:30]
  8 │     && resource.targetBranch[2] == "t"
  9 │     && resource.targetBranch[3] == "f"
    ·                              ─
 10 │     && resource.targetBranch[4] == "i"
    ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.

**Error:** invalid string literal: 4
  Example (first occurrence):
  ```
  ╭─[10:30]
  9 │     && resource.targetBranch[3] == "f"
 10 │     && resource.targetBranch[4] == "i"
    ·                              ─
 11 │     && resource.targetBranch[5] == "x"
    ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.

**Error:** invalid string literal: 5
  Example (first occurrence):
  ```
  ╭─[11:30]
 10 │     && resource.targetBranch[4] == "i"
 11 │     && resource.targetBranch[5] == "x"
    ·                              ─
 12 │     && resource.targetBranch[6] == "/"
    ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.

**Error:** invalid string literal: 6
  Example (first occurrence):
  ```
  ╭─[12:30]
 11 │     && resource.targetBranch[5] == "x"
 12 │     && resource.targetBranch[6] == "/"
    ·                              ─
 13 │ };
    ╰────
  ```
  Fix ALL occurrences of this pattern throughout your policy.


Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.