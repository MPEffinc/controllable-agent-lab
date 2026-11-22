# 2026-11-23 meeting: what can be demonstrated

## What we added and actually verified

The original Progent/AgentDojo checkout remains unchanged. A custom system-management Tool and AgentDojo `TaskSuite` were added outside it. A trusted Controller can operate on Run ID labeled, newly created Docker containers only. Source Progent `update_security_policy`, `generate_security_policy`, `apply_secure_tool_wrapper`, and `check_tool_call` remain the policy path; the Luna API request adapter is separate.

In the direct Docker harness, policy tuples such as `stop_resource: [(1, 1, {"resource_id": {"const": <owned ID>, "type": "string"}}, 0), (10, 0, {...}, 0)]` put explicit Deny ahead of Allow. The direct stop call returned Progent `POLICY_DENIED`; no Docker stop command was recorded and independent `docker inspect` stayed `running`. Allowed stop changed `running→exited`; allowed start changed `exited→running`. A broad status policy allowed a nonexistent ID through Progent, then the Controller rejected it. These are distinct Policy Deny and Backend error outcomes.

The source AgentDojo TaskSuite and Utility evaluator were connected to the trusted Docker Controller. An offline GroundTruth diagnostic produced Utility `True` for status and stop, with actual Docker state matching. It was a direct Tool Call, not a model decision. During this integration we found a real schema setup error: absent `:param resource_id:` text caused AgentDojo `make_function()` to drop that parameter. The failure was preserved and fixed, then retested.

## What is still unverified

No approved project API key was present, so `gpt-6-luna` made **zero** API requests here. We have no new Luna-generated policy, Luna-selected Tool Call, or live Progent Deny against a Luna call. The custom AgentDojo model evaluation remains blocked. Policy generation accuracy cannot be inferred from the manual-policy results.

Official Kata 4.4.0 runtime, QEMU, guest image and kernel were downloaded and checksum verified in a user directory. An independent containerd and Kata Shim ran, but guest creation failed at non-delegated host cgroup access; a separate runc attempt failed at the same cgroup boundary. No Kata guest boot, guest kernel observation, or Luna + Kata result exists. Kata's VM isolation would be a different layer from Progent's Tool-level policy even if it booted; neither amounts to OS-level policy mediation by itself. Real SSH/Proxmox VM controls and eBPF/LSM enforcement remain untested.

## Concrete next actions

1. Supply a project-specific API key via shell `OPENAI_API_KEY` or ignored `local/progent-vm/.env`; run `bash scripts/progent_vm.sh system-live --backend docker --case A` through `E`, logging each Run ID. For source AgentDojo evaluation run `bash scripts/progent_vm.sh agentdojo --backend docker --case A` through `D` separately. The code caps the local ledger at 60 requests/estimated USD 2 and each run at 2 policy requests and 5 Agent turns. Compare generated policies, actual Tool Calls, Controller entries, and final Docker state. Model access and real bill are unverified.
2. For Kata guest boot, use an approved research-only runtime with a writable delegated cgroup and UID/GID mapping helpers, or activate sudo for a dedicated runtime setup. Keep the shared daemon untouched. Then rerun Kata boot and guest/host kernel comparison before any Luna + Kata claim.

No new Research Gap is concluded from these observations. The direct Docker Deny is normal Progent behavior in its Tool Wrapper scope; broader system calls outside that wrapper were not tested.
