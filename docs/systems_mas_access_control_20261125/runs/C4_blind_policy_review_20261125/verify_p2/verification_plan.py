from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    common = {"principal_type": "User", "action": 'Action::"mergePullRequest"',
              "resource_type": "PullRequest"}
    return [
        dict(common, name="candidate_implies_gold", description="No extra permission",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(common, name="gold_implies_candidate", description="No false denial",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
