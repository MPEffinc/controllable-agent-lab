permit(principal, action == Action::"mergePullRequest", resource) when {
    principal.roles.contains(Role::"Maintainer")
    && principal != resource.author
    && action.context.onVpn
    && resource.approvalCount >= 1
    && resource.targetBranch.size() >= 7
    && resource.targetBranch.substr(0,7) == "hotfix/"
};