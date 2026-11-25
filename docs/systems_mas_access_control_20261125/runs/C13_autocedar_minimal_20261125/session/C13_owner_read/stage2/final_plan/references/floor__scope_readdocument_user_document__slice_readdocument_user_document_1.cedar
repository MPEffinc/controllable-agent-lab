permit (
  principal is User,
  action == Action::"readDocument",
  resource is Document
)
when {
    principal == resource.owner
};