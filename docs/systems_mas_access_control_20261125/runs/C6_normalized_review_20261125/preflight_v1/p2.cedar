permit (principal is User, action == Action::"mergePullRequest", resource is PullRequest)
when { (principal != resource.author) && ((resource.targetBranch like "hotfix/*")) && ((resource.approvalCount >= 1)) && (context.onVpn)) };
