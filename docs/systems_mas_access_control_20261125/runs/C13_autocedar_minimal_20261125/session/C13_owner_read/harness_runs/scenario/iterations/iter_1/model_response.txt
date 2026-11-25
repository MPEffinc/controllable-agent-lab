permit(principal, action == readDocument, resource) when
    principal is User
    && resource is Document
    && resource.owner == principal;