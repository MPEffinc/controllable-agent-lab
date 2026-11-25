permit principal action resource when
    principal is User
    && action == readDocument
    && resource is Document
    && resource.owner == principal;