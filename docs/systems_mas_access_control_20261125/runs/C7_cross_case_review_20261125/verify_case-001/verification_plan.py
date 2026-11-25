from pathlib import Path
HERE = Path(__file__).resolve().parent
def get_checks():
    common = {'principal_type': 'User', 'action': 'Action::"executeContract"', 'resource_type': 'Contract'}
    return [
        dict(common, name="normalized_implies_original", description="No extra permission",
             type="implies", reference_path=str(HERE / "reference.cedar")),
        dict(common, name="original_implies_normalized", description="No false denial",
             type="floor", floor_path=str(HERE / "reference.cedar")),
    ]
