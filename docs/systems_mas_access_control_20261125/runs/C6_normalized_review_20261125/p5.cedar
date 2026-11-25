permit (principal is User, action == Action::"mergePullRequest", resource is PullRequest)
when { (((resource.approvalCount >= 0)) && ((principal.roles.contains(Role::"Maintainer"))) && (principal != resource.author) && ((resource.targetBranch like "hotfix/*")) && (context.onVpn)) };
