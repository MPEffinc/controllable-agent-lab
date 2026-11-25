permit (principal is User, action == Action::"mergePullRequest", resource is PullRequest)
when { (((principal.roles.contains(Role::"Maintainer"))) && (principal != resource.author) && ((resource.targetBranch like "hotfix/*")) && ((resource.approvalCount >= 2)) && (context.onVpn)) };
