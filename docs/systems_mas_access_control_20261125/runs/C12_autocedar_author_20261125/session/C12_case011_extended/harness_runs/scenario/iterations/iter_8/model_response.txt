permit(principal, action == Action::"mergePullRequest", resource) when {
    principal.roles.contains(Role::"Maintainer")
    && principal != resource.author
    && action.onVpn
    && resource.approvalCount >= 1
    && resource.targetBranch.len() >= 7
    && resource.targetBranch[0] == 'h'
    && resource.targetBranch[1] == 'o'
    && resource.targetBranch[2] == 't'
    && resource.targetBranch[3] == 'f'
    && resource.targetBranch[4] == 'i'
    && resource.targetBranch[5] == 'x'
    && resource.targetBranch[6] == '/'
};