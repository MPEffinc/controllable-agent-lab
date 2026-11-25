permit(principal, action == Action::"mergePullRequest", resource) when {
    principal.roles.contains(Role::"Maintainer")
    && principal != resource.author
    && action.onVpn
    && resource.approvalCount >= 1
    && resource.targetBranch.timestamp() >= 7
    && resource.targetBranch.startsWith("hotfix/")
};