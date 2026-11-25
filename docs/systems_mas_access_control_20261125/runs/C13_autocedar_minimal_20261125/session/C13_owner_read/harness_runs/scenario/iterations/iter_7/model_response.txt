permit(principal: User, action == readDocument, resource: Document) {
    resource.owner == principal
}