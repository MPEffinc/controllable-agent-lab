permit (
  principal is User,
  action == Action::"mergePullRequest",
  resource is PullRequest
)
when {
    principal.roles.contains(Role::"Maintainer") &&
    !(principal == resource.author) &&
    context.onVpn == true
}
when { resource.approvalCount >= 1 && resource.targetBranch like "hotfix/*" };