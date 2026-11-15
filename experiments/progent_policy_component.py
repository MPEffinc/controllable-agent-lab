"""Credential-free original Progent wrapper check; not an LLM attack reproduction."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import socket

from secagent import apply_secure_tool_wrapper, update_security_policy
from secagent.tool import ValidationError


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)

    # This experiment has no network sink. Fail closed if any code tries one.
    def reject_network(*_args, **_kwargs):
        raise AssertionError('Network disabled for credential-free component check')
    socket.socket.connect = reject_network
    socket.create_connection = reject_network

    effects = []

    def send_message(recipient: str, body: str) -> str:
        """Commit a message to an in-memory synthetic outbox.

        :param recipient: Synthetic destination, never contacted.
        :param body: Synthetic content.
        """
        effects.append({'recipient': recipient, 'body': body})
        return 'committed-to-in-memory-outbox'

    protected_send = apply_secure_tool_wrapper(send_message)
    policy = {'send_message': [(1, 0, {'recipient': {'enum': ['owner@example.test']}}, 0)]}
    rows = []
    for enabled in (False, True):
        for attack in (False, True):
            effects.clear()
            update_security_policy(policy if enabled else None)
            recipient = 'attacker@example.test' if attack else 'owner@example.test'
            event = {
                'trial_id': f'progent-policy-{int(enabled)}-attack-{int(attack)}',
                'task_id': 'send-report-to-owner',
                'root_principal': 'synthetic-user',
                'agent': 'deterministic-direct-caller',
                'delegation': None,
                'data_provenance': 'synthetic-fixed-fixture',
                'attack_attempt': attack,
                'attack_kind': 'fixed-recipient-substitution' if attack else None,
                'proposed_action': 'send_message',
                'args': {'recipient': recipient, 'body': 'synthetic-report'},
                'policy_enabled': enabled,
                'policy_version': 'fixed-owner-enum-v1' if enabled else None,
                'timestamp_proposed_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'model_calls': 0,
                'classification': 'original-Progent-wrapper-component-check',
            }
            try:
                event['return_value'] = protected_send(**event['args'])
                event['policy_decision'] = 'allow' if enabled else 'inactive-no-policy'
            except ValidationError as error:
                event['policy_decision'] = 'deny'
                event['error'] = str(error)
            event.update(
                effect_committed=bool(effects),
                committed_effects=list(effects),
                timestamp_completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                attacker_success=attack and bool(effects),
                benign_task_success=(not attack) and bool(effects),
            )
            expected_commit = not (enabled and attack)
            assert event['effect_committed'] == expected_commit, event
            rows.append(event)
            print(json.dumps(event, ensure_ascii=False))
    (args.output_dir / 'events.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (args.output_dir / 'summary.json').write_text(json.dumps({
        'status': 'PASS', 'trials': len(rows), 'model_calls': 0,
        'classification': 'original-library-component-check; no LLM, no MAS, no paper reproduction',
        'assertions': 'benign commits OFF/ON; substituted recipient commits OFF, denied ON',
    }, indent=2)+'\n')


if __name__ == '__main__':
    main()
