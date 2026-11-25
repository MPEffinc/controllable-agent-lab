permit (principal is User, action == Action::"mergePullRequest", resource is PullRequest)
when { (((principal.roles.contains(Role::"Maintainer"))) && (principal != resource.author) && ((resource.approvalCount >= 1)) && (context.onVpn)) };
