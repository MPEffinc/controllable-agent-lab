permit(principal: User, action == readDocument, resource: Document)
  when resource.owner == principal;