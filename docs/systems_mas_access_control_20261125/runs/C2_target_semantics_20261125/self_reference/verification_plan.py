"""Research-authored plan, not an AutoCedar generated target."""
from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    common = {"principal_type": "User", "action": 'Action::"mergePullRequest"',
              "resource_type": "PullRequest"}
    return [
        dict(common, name="candidate_implies_target", description="Candidate within target",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(common, name="target_implies_candidate", description="Candidate covers target",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
