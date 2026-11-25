permit(
    principal == User::"student",
    action == Action::"read",
    resource == Document::"doc"
);

forbid(
    principal == User::"student",
    action == Action::"read",
    resource == Document::"doc"
) when { !context.registration_open };
