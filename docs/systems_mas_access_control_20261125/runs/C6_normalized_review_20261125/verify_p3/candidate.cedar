permit (principal is User, action == Action::"mergePullRequest", resource is PullRequest)
when { (((principal.roles.contains(Role::"Maintainer"))) && ((resource.targetBranch like "hotfix/*")) && ((resource.approvalCount >= 1)) && (context.onVpn)) };
