from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    merge = {"principal_type": "User", "action": 'Action::"mergePullRequest"',
             "resource_type": "PullRequest"}
    checks = [
        dict(merge, name="merge_candidate_implies_gold", description="No extra merge",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(merge, name="gold_implies_merge_candidate", description="No missing merge",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
    pass
    return checks
