# AutoCedar Approved Intent Target

This Stage 3 specification is generated from HITL/AITL-approved schema and property atoms. The raw input document remains archived as `requirement.md` in the session input directory, but policy synthesis must satisfy the reviewed formal target below rather than reinterpreting the raw prose.

## Approved Schema Atoms
- supplied schema; no Stage 1 atoms

## Approved Property Atoms
- Req0002MergePullRequestUserPullRequestCondition [condition]: A user may merge a pull request only if they have the maintainer role, are not the author of the pull request, and are connected to the VPN. (action=mergePullRequest; principals=User; resources=PullRequest; source_ids=src.root.p0002.l3; source=[source_id: src.root.p0002.l3] A user may merge a pull request only if the user holds the maintainer role, is not the pull request’s author, and is using the VPN.)
- Req0003MergePullRequestUserPullRequestCondition [condition]: The pull request must have at least one approval and its target branch name must begin with "hotfix/". (action=mergePullRequest; principals=User; resources=PullRequest; source_ids=src.root.p0003.l3; source=[source_id: src.root.p0003.l3] The pull request must have at least one approval, and its target branch name must begin with “hotfix/”.)
- floor__scope_mergepullrequest_user_pullrequest__slice_mergepullrequest_user_pullrequest_1 [floor]: Requests in slice 'User holds maintainer role, is not author of the pull request, uses VPN, pull request has approval and target branch starts with 'hotfix/'.' must be allowed. (action=mergePullRequest; principals=User; resources=PullRequest; source_ids=src.root.p0002.l3, src.root.p0003.l3; source=[source_id: src.root.p0002.l3] [source_id: src.root.p0003.l3])
- ceiling__scope_mergepullrequest_user_pullrequest [ceiling]: Only requests in one of this scope's slices may be allowed. (action=mergePullRequest; principals=User; resources=PullRequest; source_ids=src.root.p0002.l3, src.root.p0003.l3; source=[source_id: src.root.p0002.l3] [source_id: src.root.p0003.l3])
