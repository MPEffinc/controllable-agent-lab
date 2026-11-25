## Verification Results — 1 check(s) FAILED

- validation (validation): **FAIL**
**TYPE-CHECK / VALIDATION ERROR — your policy parses, but Cedar's validator rejected it.**
This is NOT a parse error. Do NOT change `principal is User` or rule structure.
Cedar's type-checker found that your policy could fail at runtime.

Raw validator output:
```
× policy set validation failed
  ╰─▶ the types Long and String are not compatible
   ╭─[6:8]
 5 │     && resource.approvalCount >= 1
 6 │     && resource.targetBranch == "hotfix/" + resource.targetBranch.offset(7)
   ·        ────────────────────────────────────────────────────────────────────
 7 │ };
   ╰────
  help: for policy `policy0`, both operands to a `==` expression must have
        compatible types. Types must be exactly equal to be compatible

Error: 
  × for policy `policy0`, unexpected type: expected Long but saw String
   ╭─[6:33]
 5 │     && resource.approvalCount >= 1
 6 │     && resource.targetBranch == "hotfix/" + resource.targetBranch.offset(7)
   ·                                 ─────────
 7 │ };
   ╰────
  help: Cedar does not support string concatenation

Error: 
  × for policy `policy0`, attribute `context` on entity type `Action` not
  │ found
   ╭─[4:8]
 3 │     && principal != resource.author
 4 │     && action.context.onVpn
   ·        ────────────────────
 5 │     && resource.approvalCount >= 1
   ╰────

Error: 
  × for policy `policy0`, unexpected type: expected datetime but saw String
   ╭─[6:45]
 5 │     && resource.approvalCount >= 1
 6 │     && res
... (790 more characters truncated)
```

Fix the policy to address EVERY failure without breaking passing checks. Output the COMPLETE updated policy.