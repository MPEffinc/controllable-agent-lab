"""Scripted adversary actions for R2 (white-box, deterministic, NOT adaptive, no LLM).

Boundary on purpose: this module imports NOTHING from trusted.py. Every function
receives only what an attacker may hold:
  * public information (trusted signer id, sink id, the evidence in its hands),
  * a signer the attacker legitimately owns (its own hosted stage key, or key:rogue).
It cannot reach the RuntimeState authority, the permit service's key, the issuer
keys or the world. Each action corresponds to a fault the ORIGINAL artifact
already defines (POST_PERMIT_ACTION_SUBSTITUTION, ALTERNATE_PATH, forged permit,
tampered/missing proof); R2 asks whether the same defences hold when the move is
made by a delegated agent reached through A2A hops and a queue.
"""
from __future__ import annotations

import dataclasses
import json

from continuity.core import ExecutionPermit, ProofBundle, digest


def substitute_action(action, substitution):
    """POST_PERMIT_ACTION_SUBSTITUTION (workspace flavour of the original _execution_action)."""
    parameters = dict(action.parameters)
    parameters['body'] = parameters['body'] + substitution['body_suffix']
    return dataclasses.replace(action, destination=substitution['destination'], parameters=parameters)


def strip_proof(bundle: ProofBundle) -> ProofBundle:
    """Present a bundle without its envelope chain and receipts (missing proof)."""
    return dataclasses.replace(bundle, envelopes=(), receipts=())


def forge_permit(bundle: ProofBundle, action, own_signer, sink_id, claimed_signer_id=None):
    """Mint an ExecutionPermit with a key the attacker owns.

    claimed_signer_id=None  -> honest-looking forgery: signer field is the attacker key.
    claimed_signer_id=<id>  -> claims the trusted permit signer but signs with the attacker key.
    """
    ctx = bundle.envelopes[-1].context
    permit = ExecutionPermit(
        permit_id=f'permit:forged:{digest(action)[-16:]}', principal=ctx.principal, subject=ctx.actor,
        task_root=ctx.task_root, grant_id=ctx.root_grant_id, audience=sink_id,
        action_digest=action.action_digest, bundle_digest=digest(bundle), policy_id=ctx.policy_id,
        policy_digest=ctx.policy_digest, policy_epoch=ctx.policy_epoch, nonce=ctx.nonce,
        idempotency_key=f'{ctx.task_root}:{action.action_digest}', expires_at=ctx.expires_at,
        one_time=True, signer=claimed_signer_id or own_signer.key_id)
    return dataclasses.replace(permit, signature=own_signer.sign(permit.unsigned()))


def tamper_wire(bundle_wire: str, tamper) -> str:
    """The untrusted queue rewrites a field of the retained evidence without re-signing."""
    data = json.loads(bundle_wire)
    envelope = data['envelopes'][tamper['envelope_index']]
    node = envelope
    *path, leaf = tamper['field'].split('.')
    for key in path:
        node = node[key]
    node[leaf] = tamper['value']
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
