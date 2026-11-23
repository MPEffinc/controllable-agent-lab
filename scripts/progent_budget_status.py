"""Read the local API request ledger without loading credentials or making requests."""

import json

from scripts.progent_system_live import LEDGER, MAX_REQUESTS


def main() -> None:
    state = json.loads(LEDGER.read_text()) if LEDGER.exists() else {"requests": 0, "reserved_usd": 0.0}
    used = int(state["requests"])
    reserved = float(state["reserved_usd"])
    print(f"[API REQUESTS] {used}/{MAX_REQUESTS}; remaining {max(0, MAX_REQUESTS - used)}")
    print(f"[LOCAL RESERVED ESTIMATE] USD {reserved:.6f} / 2.000000")
    print("[ACTUAL BILL] NOT CHECKED")


if __name__ == "__main__":
    main()
