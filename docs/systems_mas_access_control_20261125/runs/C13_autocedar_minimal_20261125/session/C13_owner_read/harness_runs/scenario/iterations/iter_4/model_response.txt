permit(principal, action, resource) {
  principal is User
  && action == readDocument
  && resource is Document
  && resource.owner == principal
}