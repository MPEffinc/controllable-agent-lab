"""R3: a three-agent A2A chain (A -> B -> C) around the ORIGINAL CONTINUITY.

Reuses the R2 adapter unchanged: trusted.py (trusted plane and stage hosts),
adversary.py, proof_codec.py and the R2 Trial class (event log, A2A send,
revocation, handler dispatch). Only the agent set, the stage placement
(memory@A, gateway@B, adapter@C) and the schedules are new.

SYNTHETIC MULTI-AGENT EXPERIMENT. Official a2a-sdk over in-process ASGI (no
sockets), deterministic sequential schedule, scripted behaviour, no LLM, no paid
API. A->B->C is WORK delegation: every RootGrant names C as actor at issuance, so
no authority is delegated by A or B. Conditions whose authorization semantics
CONTINUITY does not define (G3-G5) are NOT run here (see config.json).
Outcomes are not asserted: expectations live in config.json and are compared by
classify.py; correctness is judged by the independent oracle.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import socket
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R2 = ROOT / 'experiments/r2'
sys.path.insert(0, str(R2))  # trusted, adversary and proof_codec have unique names


def load_by_path(name, path):
    """Load a module under a unique name so same-named R2 and R3 files never collide."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


r2s = load_by_path('r2_scenario', R2 / 'scenario.py')  # imports trusted first (pinned original check)
import proof_codec as codec  # noqa: E402  (R2 module)
from trusted import ProofBundle, StageHost, digest  # noqa: E402

utc = r2s.utc


class Trial3(r2s.Trial):
    """Three agents. Same attribute contract as the R2 Trial, so emit/send/revoke/handle are reused."""

    def __init__(self, cfg, spec, trial_id, stream):
        self.cfg, self.spec, self.trial_id, self.stream = cfg, spec, trial_id, stream
        self.events = []
        self.queue = asyncio.Queue()
        self.plane = r2s.TrustedPlane(cfg, self.emit, spec.get('ablation', []))
        # Original 3-stage pipeline, one stage per agent (each shim holds only its own stage key).
        self.hosts = {'agent-A': StageHost(self.plane, 'agent-A', ('memory',)),
                      'agent-B': StageHost(self.plane, 'agent-B', ('gateway',)),
                      'agent-C': StageHost(self.plane, 'agent-C', ('adapter',))}
        self.materials, self.held = {}, {}
        self.adapter_errors, self.tampered, self.protocol_messages = 0, False, 0
        self.ops = {('agent-A', 'delegate'): self.a_delegate, ('agent-B', 'relay'): self.b_relay,
                    ('agent-C', 'execute'): self.c_execute, ('agent-C', 'prepare'): self.c_prepare,
                    ('agent-C', 'commit'): self.c_commit}
        self.agents = {
            name: r2s.OfficialA2AFunctionAgent(
                agent={'agent_id': name, 'name': name, 'capabilities': ['r3-continuity-work-delegation']},
                handler=lambda payload, agent_id=name: self.handle(agent_id, payload))
            for name in ('agent-A', 'agent-B', 'agent-C')}

    # ---------------- agent side (UNTRUSTED logic, scripted; honest in every R3 condition) ----------------
    def note_delegation(self, agent_id, payload):
        """Record who handed the work over. This is WORK delegation; authority evidence is always NONE."""
        self.emit('delegation_context', agent_id, work_id=payload['work_id'], current_actor=agent_id,
                  delegating_actor=payload.get('from_agent', 'ingress'), delegation_kind='WORK_DELEGATION',
                  authority_delegation_evidence='NONE')

    def forward3(self, agent_id, payload, bundle, destination, operation):
        work_id = payload['work_id']
        self.emit('delegation_requested', agent_id, work_id=work_id, destination_agent=destination,
                  delegating_actor=agent_id, delegation_kind='WORK_DELEGATION',
                  bundle_digest=digest(bundle), receipts=len(bundle.receipts))
        self.queue.put_nowait(dict(destination=destination, operation=operation, work_id=work_id,
                                   bundle=codec.to_wire(bundle), from_agent=agent_id,
                                   final_operation=payload.get('final_operation', 'execute')))
        self.emit('queue_enqueued', agent_id, work_id=work_id, destination_agent=destination,
                  queue_size=self.queue.qsize(), reason='queue_acceptance_is_not_effect_finality')

    def a_delegate(self, agent_id, payload):
        self.note_delegation(agent_id, payload)
        bundle = codec.from_wire(ProofBundle, payload['bundle'])
        self.forward3(agent_id, payload, self.hosts[agent_id].apply(bundle, 'memory'), 'agent-B', 'relay')
        return {'status': 'queued', 'work_id': payload['work_id']}

    def b_relay(self, agent_id, payload):
        self.note_delegation(agent_id, payload)
        bundle = codec.from_wire(ProofBundle, payload['bundle'])
        self.forward3(agent_id, payload, self.hosts[agent_id].apply(bundle, 'gateway'), 'agent-C',
                      payload.get('final_operation', 'execute'))
        return {'status': 'queued', 'work_id': payload['work_id']}

    def c_bundle(self, agent_id, payload):
        self.note_delegation(agent_id, payload)
        bundle = codec.from_wire(ProofBundle, payload['bundle'])
        return self.hosts[agent_id].apply(bundle, 'adapter')

    def c_execute(self, agent_id, payload):
        bundle = self.c_bundle(agent_id, payload)
        decision, permit = self.plane.request_permit(bundle, agent_id)
        result = {'status': 'completed', 'allowed': bool(decision and decision.allowed)}
        if permit is not None:
            ok, reason, _ = self.plane.dispatch(agent_id, self.final_action(bundle), permit)
            result.update(dispatch_ok=ok, dispatch_reason=reason)
        return result

    def c_prepare(self, agent_id, payload):
        bundle = self.c_bundle(agent_id, payload)
        decision, permit = self.plane.request_permit(bundle, agent_id)
        self.held[payload['work_id']] = (permit, self.final_action(bundle))
        return {'status': 'completed', 'allowed': bool(decision and decision.allowed),
                'permit_held': permit is not None}

    def c_commit(self, agent_id, payload):
        permit, action = self.held.pop(payload['work_id'], (None, None))
        if permit is None:
            return {'status': 'completed', 'dispatch': 'NO_HELD_PERMIT'}
        ok, reason, _ = self.plane.dispatch(agent_id, action, permit)
        return {'status': 'completed', 'dispatch_ok': ok, 'dispatch_reason': reason}

    # ---------------- harness (user, scheduler) ----------------
    async def send_a(self, label, final_operation='execute'):
        bundle, _ = self.materials[label]
        await self.send('agent-A', 'delegate', work_id=f'{self.trial_id}-work-{label}',
                        bundle=codec.to_wire(bundle), final_operation=final_operation, from_agent='ingress')

    async def drain(self, max_steps=None):
        steps = 0
        while not self.queue.empty() and (max_steps is None or steps < max_steps):
            entry = self.queue.get_nowait()
            self.emit('queue_dequeued', 'harness', work_id=entry['work_id'],
                      destination_agent=entry['destination'], queue_size=self.queue.qsize())
            await self.send(entry['destination'], entry['operation'], work_id=entry['work_id'],
                            bundle=entry['bundle'], from_agent=entry['from_agent'],
                            final_operation=entry['final_operation'])
            self.queue.task_done()
            steps += 1
        return steps

    async def run(self):
        spec, family = self.spec, self.spec['family']
        self.emit('trial_started', 'harness', configuration=spec, group=spec['group'],
                  ablation=spec.get('ablation', []),
                  trusted_permit_signer=self.plane.public_info()['trusted_permit_signer_id'],
                  policy_epoch=self.cfg['policy_epoch'], sink_id=self.plane.sink_id,
                  agent_identities={k: v['identity'] for k, v in self.cfg['agents'].items()},
                  oracle_semantics='IMMEDIATE_CUT_AT_FINALITY', original_sha=self.cfg['original_method']['pinned_sha'],
                  scheduler='deterministic_sequential_queue_schedule; no races',
                  delegation_model='WORK_DELEGATION_ONLY; every RootGrant names agent-C as actor at issuance')
        for material in spec['materials']:  # every root is issued at trial start (as in R1 and R2)
            bundle, entry = self.plane.issue_material(material, material['label'])
            self.materials[material['label']] = (bundle, entry)
            grant = bundle.root_grant
            self.emit('grant_record', 'trusted-issuer', material_label=material['label'], grant_id=grant.grant_id,
                      root_principal=grant.principal, grant_issuer=grant.issuer, grant_actor=grant.actor,
                      support_kind='ROOT', parent_support=None, independent_supports=[],
                      authority_delegation_evidence='NONE',
                      note='CONTINUITY RootGrant has no parent reference; a separately signed grant is an independent root')
        if family == 'chain_normal':
            await self.send_a('rootA')
            await self.drain()
        elif family == 'chain_inflight_revoke':
            await self.send_a('rootA', final_operation='prepare')
            await self.drain()  # C hosts the adapter stage and obtains (holds) a permit
            self.revoke('rootA')
            await self.send('agent-C', 'commit', work_id=f'{self.trial_id}-work-rootA')
        elif family == 'chain_retained_revoke':
            await self.send_a('rootA')
            await self.drain(max_steps=1)  # B relays; the work is now retained for C
            self.revoke('rootA')
            await self.drain()
        elif family == 'chain_independent_root':
            await self.send_a('rootA')
            await self.drain(max_steps=1)
            self.revoke('rootA')
            await self.drain()  # C processes the rootA work after the cut
            await self.send_a('rootX')
            await self.drain()
        else:
            raise ValueError(f'unknown family {family}')
        verifier = [dict(by=e['requester'], allowed=e['allowed'], reason_codes=e['reason_codes'])
                    for e in self.events if e['event_type'] == 'verify_decision']
        attempts = [dict(caller=e['caller_agent'], ok=e['result_ok'], reason=e['result_reason'])
                    for e in self.events if e['event_type'] == 'finality_attempt']
        hops = [[e['stage'], e['source']] for e in self.events if e['event_type'] == 'hop_applied']
        out = dict(trial_id=self.trial_id, condition_id=spec['id'], group=spec['group'], family=family,
                   event_count=len(self.events) + 1, observed_verifier_decisions=verifier,
                   observed_finality_attempts=attempts, observed_hops=hops,
                   world_effect_count=len(self.plane.world.effects), adapter_errors=self.adapter_errors,
                   a2a_messages=self.protocol_messages, classification=r2s.CLASSIFICATION,
                   oracle_result='NOT_OBSERVED', model_calls=0)
        self.emit('trial_completed', 'harness', observed_summary=out,
                  reason='observed_counts_only; independent oracle and expectation check are separate programs')
        return out


async def run_all(cfg, output_dir):
    summaries, worlds = [], {}
    runnable = [c for c in cfg['conditions'] if c['execution'] == 'RUN']
    with (output_dir / 'events.jsonl').open('x') as stream:
        for spec in runnable:
            trial = Trial3(cfg, spec, f'{spec["id"]}-r1', stream)
            try:
                summaries.append(await trial.run())
                worlds[trial.trial_id] = trial.plane.snapshot()
            finally:
                await trial.close()
    return summaries, worlds


def git_out(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--config', type=Path, default=HERE / 'config.json')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    config_rel = str(args.config.resolve().relative_to(ROOT))
    if subprocess.call(['git', 'diff', '--quiet', 'HEAD', '--', config_rel], cwd=ROOT) != 0:
        sys.exit('config differs from the committed (pre-registered) version; commit the change with a reason first')
    args.output_dir.mkdir(parents=True, exist_ok=False)
    cfg = json.loads(args.config.read_text())

    def no_socket_connect(*_args, **_kwargs):
        raise RuntimeError('R3 forbids network socket connect (in-process ASGI transport only)')
    socket.socket.connect = no_socket_connect
    socket.create_connection = no_socket_connect

    summaries, worlds = asyncio.run(run_all(cfg, args.output_dir))
    summary = dict(classification=r2s.CLASSIFICATION, fixture='official_A2A_SDK_inprocess_transport_plus_original_CONTINUITY_three_agents',
                   original_paper_reproduction=False, model_calls=0, trial_count=len(summaries), trials=summaries)
    (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (args.output_dir / 'world_state.json').write_text(json.dumps(worlds, indent=2) + '\n')

    def sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    cdir, adir = ROOT / 'third_party/continuity', ROOT / 'third_party/a2asecbench'
    versions = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
    manifest = dict(
        created_utc=utc(), python=sys.version, package_versions=versions,
        parent_commit=git_out('rev-parse', 'HEAD'),
        config_last_commit=git_out('log', '-n1', '--format=%H', '--', config_rel),
        tracked_files_dirty=bool(git_out('status', '--porcelain', '--untracked-files=no')),
        uncommitted_code_paths=git_out('status', '--porcelain', '--', 'experiments/r3', 'experiments/r2', 'scripts').splitlines(),
        code_sha256={'r3/scenario.py': sha(HERE / 'scenario.py'),
                     **{f'r2/{n}': sha(R2 / n) for n in ('scenario.py', 'trusted.py', 'adversary.py', 'proof_codec.py')}},
        config_sha256=sha(args.config),
        original_continuity=dict(
            repository='https://github.com/zast-ai/continuity', head=git_out('rev-parse', 'HEAD', cwd=cdir),
            working_tree_clean=not git_out('status', '--porcelain', cwd=cdir),
            file_sha256={f'src/continuity/{n}': sha(cdir / 'src/continuity' / n) for n in ('core.py', 'experiment.py')}),
        reused_a2a_helper=dict(head=git_out('rev-parse', 'HEAD', cwd=adir),
                               file_sha256={'harness/a2a_lab/sdk_protocol.py': sha(adir / 'harness/a2a_lab/sdk_protocol.py')}),
        events_sha256=sha(args.output_dir / 'events.jsonl'), world_state_sha256=sha(args.output_dir / 'world_state.json'),
        summary_sha256=sha(args.output_dir / 'summary.json'))
    (args.output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for trial in summaries:
        print(json.dumps({k: trial[k] for k in ('trial_id', 'observed_verifier_decisions', 'observed_finality_attempts',
                                                'world_effect_count', 'adapter_errors')}, ensure_ascii=False))
    print(json.dumps({'trial_count': len(summaries), 'event_file': str(args.output_dir / 'events.jsonl'),
                      'oracle_result': 'NOT_OBSERVED; run the independent oracle separately'}))


if __name__ == '__main__':
    main()
