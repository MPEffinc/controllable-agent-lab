// Policy store — verified policies appended here

// --- Verified (eval iteration 12) ---
permit(principal, action == Action::"readDocument", resource) when { resource.owner == principal };
