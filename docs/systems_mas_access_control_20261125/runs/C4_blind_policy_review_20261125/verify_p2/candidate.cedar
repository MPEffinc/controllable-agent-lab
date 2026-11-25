permit (principal is User, action == Action::"mergePullRequest", resource is PullRequest)
when { (((resource.approvalCount >= 0)) && (!(true) || (principal != resource.author)) && ((resource.targetBranch like "hotfix/*")) && ((resource.approvalCount >= 1)) && (context.onVpn)) };
