permit(principal, action == mergePullRequest, resource) when {
    principal.roles.contains("Maintainer")
    && principal != resource.author
    && action.context.onVpn
    && resource.approvalCount >= 1
    && resource.targetBranch.startsWith("hotfix/")
};