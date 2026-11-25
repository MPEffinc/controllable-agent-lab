permit(
    principal == User::"student",
    action == Action::"read",
    resource == Document::"doc"
) when { context.registration_open };

permit(
    principal == User::"student",
    action == Action::"read",
    resource == Document::"doc"
) when { context.alternate_allow };

forbid(
    principal == User::"student",
    action == Action::"read",
    resource == Document::"doc"
) when { context.embargo_active };
