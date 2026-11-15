"""Trusted plane of the R2 adapter around the ORIGINAL CONTINUITY (pinned SHA).

This module is ADAPTER code. It never reimplements, weakens or bypasses a
CONTINUITY check; every security decision below is made by original code:
  ContinuityVerifier.verify_bundle / issue_permit,
  EffectBroker.dispatch, FinalitySink.execute, Component.apply, make_scenario.
What the adapter adds is only WHEN and WITH WHICH STATE the originals are called:
  * the verifier is rebuilt on every call with the CURRENT RuntimeState,
  * the sink receives the CURRENT RuntimeState, the caller identity bound to the
    A2A handler (never the payload) and a trusted clock,
  * the sink's SimulatedWorld is the single effect sink.
Agents never receive a Signer of a trusted issuer, the RuntimeState authority or
the world. This is an in-process separation (no OS isolation); see
docs/R2_SEMANTIC_ALIGNMENT.md section 4.4.
"""
from __future__ import annotations

import dataclasses
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTINUITY_DIR = ROOT / 'third_party/continuity'
PINNED_SHA = '59cfe60930d247d1890b366ded686c718020a11e'


def _git(*args):
    return subprocess.check_output(['git', '-C', str(CONTINUITY_DIR), *args], text=True).strip()


def verify_original_unmodified():
    """Refuse to run unless the original artifact is the pinned, unmodified checkout."""
    head = _git('rev-parse', 'HEAD')
    if head != PINNED_SHA:
        raise RuntimeError(f'original CONTINUITY is at {head}, expected pinned {PINNED_SHA}')
    dirty = _git('status', '--porcelain')
    if dirty:
        raise RuntimeError('original CONTINUITY checkout has local modifications:\n' + dirty)
    return head


verify_original_unmodified()
sys.dont_write_bytecode = True  # keep the pinned checkout free of generated files
sys.path.insert(0, str(CONTINUITY_DIR / 'src'))

from continuity.core import (  # noqa: E402  (original code, imported unmodified)
    Component, ContinuityVerifier, Decision, EffectBroker, ExecutionPermit, FinalitySink,
    NonceLedger, ProofBundle, RuntimeState, SimulatedWorld, TransformResult, digest,
)
from continuity.experiment import (  # noqa: E402
    NOW, _alias_witness, _representation_transform, build_infrastructure, make_scenario,
)
import proof_codec as codec  # noqa: E402

PROTOCOLS = {'memory': 'memory', 'gateway': 'policy', 'adapter': 'mcp-jsonrpc'}


class AdapterError(RuntimeError):
    """Misuse of the adapter itself (never a CONTINUITY decision)."""


class TrustedPlane:
    """Everything an agent must not control, bound to ONE trial."""

    def __init__(self, cfg, emit, ablation=frozenset()):
        if cfg['now'] != NOW:
            raise AdapterError('config clock differs from the original NOW')
        self.cfg, self.emit, self.ablation = cfg, emit, frozenset(ablation)
        self.infra = build_infrastructure()  # original deployment, contracts, keys
        if self.infra.deployment.runtime_state.policy_epoch != cfg['policy_epoch']:
            raise AdapterError('config policy epoch differs from the original deployment')
        self.domain = cfg['domain']
        self.now = NOW
        self.sink_id = f'spiffe://example/finality/{self.domain}'
        self.state: RuntimeState = self.infra.deployment.runtime_state
        self.world, self.ledger = SimulatedWorld(), NonceLedger()
        a = self.ablation
        # Same mapping as the original run_system(): ablation names -> original flags.
        self.sink = FinalitySink(
            self.sink_id, self.infra.keyring, self.infra.signers['verifier'].key_id,
            self.infra.signers['sink'], self.ledger, self.world,
            enforce_action_binding='action_binding' not in a,
            enforce_subject_binding='subject_binding' not in a,
            enforce_policy_freshness='policy' not in a,
            enforce_revocation='revocation' not in a,
            enforce_nonce='replay' not in a,
            enforce_idempotency='replay' not in a)
        self.broker = EffectBroker(self.sink, require_permit='mediation' not in a)
        self.directory = {}       # logical alias -> (resolved destination, witness id)
        self.roots = {}           # task_root -> grant_id  (issuer ledger)
        self.issued_permits = {}  # permit_id -> grant_id  (what this service really issued)

    # ---- public (non-secret) information an attacker may read ----
    def public_info(self):
        return {'trusted_permit_signer_id': self.infra.signers['verifier'].key_id,
                'sink_id': self.sink_id}

    # ---- issuance (trusted authority / ingress / provenance / context) ----
    def issue_material(self, spec, label):
        """Create the root evidence with the ORIGINAL generator and log the issuer ledger."""
        sc = make_scenario(self.domain, spec['seed'], spec['kind'], fault=spec['fault'], infra=self.infra)
        self.directory[sc.initial.action.destination] = (sc.resolved_destination, f'witness:{sc.scenario_id}')
        root = ProofBundle(sc.root_grant, sc.provenance_manifest, sc.context_manifest,
                           sc.release_credentials, (), (sc.initial,), ())
        if spec['issuer'] == 'attacker':
            # Evidence minted with the attacker-owned key: nothing enters the issuer ledger.
            self.emit('attacker_material_created', 'attacker', material_label=label, seed=spec['seed'],
                      kind=spec['kind'], fault=spec['fault'], root_envelope_producer=sc.initial.producer,
                      root_grant_issuer=sc.root_grant.issuer)
            return root, None
        # Authorized effect = benign twin of the same seed (config: authorization_rules).
        twin = make_scenario(self.domain, spec['seed'], 'benign', infra=self.infra)
        agents = self.cfg['agents']
        expected_actor = agents[spec['authorized_actor']]['identity']
        if sc.root_grant.actor != expected_actor:
            raise AdapterError(f'material {label}: grant actor {sc.root_grant.actor} != configured {expected_actor}')
        a = twin.initial.action
        entry = dict(grant_id=sc.root_grant.grant_id, root_task_id=sc.root_grant.task_root,
                     principal_id=sc.root_grant.principal, authorized_actor=spec['authorized_actor'],
                     actor_identity=expected_actor, completion_expected=spec['completion_expected'],
                     authorized_effect=dict(operation=a.operation, resource=a.resource,
                                            destination=twin.resolved_destination,
                                            parameters=dict(a.parameters), effect_class=a.effect_class))
        self.roots[sc.root_grant.task_root] = sc.root_grant.grant_id
        self.emit('grant_issued', 'trusted-issuer', material_label=label, seed=spec['seed'],
                  kind=spec['kind'], fault=spec['fault'], **entry)
        return root, entry

    # ---- runtime state authority ----
    def revoke(self, task_root):
        grant_id = self.roots[task_root]
        self.state = dataclasses.replace(self.state, revoked_ids=self.state.revoked_ids | {grant_id})
        self.emit('revoke', 'trusted-state-authority', root_task_id=task_root, grant_id=grant_id,
                  state_revoked_ids=sorted(self.state.revoked_ids))

    # ---- directory (trusted transform issuer for alias resolution) ----
    def alias_witness(self, before_envelope, after_envelope, contract_id, witness_id):
        return _alias_witness(self.infra, before_envelope, after_envelope,
                              self.infra.signers['directory'], contract_id, witness_id)

    # ---- permit service: original verify_bundle + issue_permit with CURRENT state ----
    def _verifier(self):
        deployment = dataclasses.replace(self.infra.deployment, runtime_state=self.state)
        return ContinuityVerifier(self.infra.keyring, self.infra.contracts, deployment,
                                  self.infra.signers['verifier'], self.ablation)

    def request_permit(self, bundle: ProofBundle, requester: str):
        """Return (Decision, ExecutionPermit | None). Fail-closed on any adapter exception."""
        try:
            verifier = self._verifier()
            decision = verifier.verify_bundle(bundle, self.now)
            permit = None
            if decision.allowed:
                permit = verifier.issue_permit(decision, bundle.envelopes[-1], self.sink_id, self.now)
        except Exception as error:  # noqa: BLE001 - recorded, never silently allowed
            self.emit('adapter_exception', 'permit-service', requester=requester,
                      error=f'{type(error).__name__}: {error}')
            return None, None
        self.emit('verify_decision', 'permit-service', requester=requester, allowed=decision.allowed,
                  reason_codes=list(decision.reason_codes), bundle_digest=decision.bundle_digest,
                  action_digest=decision.action_digest, grant_id=decision.grant_id,
                  state=dict(policy_epoch=self.state.policy_epoch, revoked_ids=sorted(self.state.revoked_ids)))
        if permit is not None:
            self.issued_permits[permit.permit_id] = permit.grant_id
            self.emit('permit_issued', 'permit-service', requester=requester,
                      **{k: v for k, v in codec.encode(permit).items() if k != 'signature'})
        return decision, permit

    # ---- effect gateway: original EffectBroker.dispatch with CURRENT state ----
    def dispatch(self, caller_agent, action, permit):
        caller_identity = self.cfg['agents'][caller_agent]['identity']  # bound to the handler
        before = len(self.world.effects)
        ok, reason, outcome = self.broker.dispatch(action, permit, self.now, caller_identity, self.state)
        after = len(self.world.effects)
        self.emit('finality_attempt', 'effect-gateway', caller_agent=caller_agent,
                  caller_identity=caller_identity, action=codec.encode(action),
                  permit=(None if permit is None else
                          {k: v for k, v in codec.encode(permit).items() if k != 'signature'}),
                  state=dict(policy_epoch=self.state.policy_epoch, revoked_ids=sorted(self.state.revoked_ids)),
                  result_ok=ok, result_reason=reason, new_effect=after > before,
                  effect_id=(f'effect:{before}' if after > before else None),
                  world_effect_count_after=after)
        return ok, reason, outcome

    def snapshot(self):
        return dict(effects=[dict(e, parameters=dict(e['parameters'])) for e in self.world.effects],
                    consumed_nonces=sorted(self.ledger.consumed_nonces),
                    outcome_keys=sorted(self.ledger.outcomes),
                    revoked_ids=sorted(self.state.revoked_ids))


class StageHost:
    """Trusted shim co-located with an agent: applies ORIGINAL Component stages.

    It holds only the stage keys of the stages this agent hosts. The agent's
    own logic may supply a `logic` callable that transforms the envelope; the
    original verifier later rejects any transformation the contracts forbid.
    """

    def __init__(self, plane: TrustedPlane, agent_id: str, hosted_stages):
        self.plane, self.agent_id, self.hosted = plane, agent_id, tuple(hosted_stages)

    def held_signer(self, stage):
        if stage not in self.hosted:
            raise AdapterError(f'{self.agent_id} does not hold the key of stage {stage}')
        return self.plane.infra.signers[stage]

    def apply(self, bundle: ProofBundle, stage: str, logic=None) -> ProofBundle:
        deployment = self.plane.infra.deployment
        index = len(bundle.receipts)
        if stage not in self.hosted:
            raise AdapterError(f'{self.agent_id} does not host stage {stage}')
        if index >= len(deployment.pipeline) or deployment.pipeline[index].stage != stage:
            raise AdapterError(f'stage {stage} is out of order at position {index}')
        contract = self.plane.infra.contracts[deployment.pipeline[index].contract_id]
        plane = self.plane

        def benign(envelope):
            out = _representation_transform(PROTOCOLS[stage])(envelope)
            witnesses = ()
            if stage == 'adapter':
                hit = plane.directory.get(envelope.action.destination)
                if hit is not None:
                    resolved, witness_id = hit
                    out = dataclasses.replace(out, action=dataclasses.replace(out.action, destination=resolved))
                    witnesses = (plane.alias_witness(envelope, out, contract.contract_id, witness_id),)
            return TransformResult(out, witnesses)

        component = Component(stage, contract, self.held_signer(stage), logic or benign)
        out, receipt, witnesses = component.apply(bundle.envelopes[-1])
        result = dataclasses.replace(
            bundle, envelopes=bundle.envelopes + (out,), receipts=bundle.receipts + (receipt,),
            transformation_witnesses=bundle.transformation_witnesses + witnesses)
        plane.emit('hop_applied', self.agent_id, stage=stage, signer=receipt.signer,
                   input_digest=receipt.input_digest, output_digest=receipt.output_digest,
                   changed_fields=list(receipt.changed_fields), witnesses=len(witnesses))
        return result
