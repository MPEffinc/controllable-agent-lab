"""R2: original CONTINUITY wired into the R1 A2A delegation path (Agent A -> queue -> Agent B).

SYNTHETIC MULTI-AGENT EXPERIMENT. Official a2a-sdk AgentCard/JSON-RPC over an
in-process ASGI transport (no sockets); deterministic sequential schedule (no
races); scripted white-box agent behaviours (no LLM, no paid API). Every security
decision is made by the pinned, unmodified CONTINUITY code through trusted.py.
Outcomes are NOT asserted here: expected results live in config.json and are
compared later by classify.py; correctness is judged by the independent oracle.
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import datetime as dt
import hashlib
import importlib.metadata
import json
import socket
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'third_party/a2asecbench'))
from harness.a2a_lab.sdk_protocol import OfficialA2AFunctionAgent  # noqa: E402  original, unmodified helper

from trusted import ProofBundle, StageHost, TrustedPlane, digest  # noqa: E402  (verifies the pinned original first)
import adversary  # noqa: E402  (needs the original on sys.path, set by trusted.py)
import proof_codec as codec  # noqa: E402

CLASSIFICATION = 'SYNTHETIC_MULTI_AGENT_EXPERIMENT_WITH_ORIGINAL_CONTINUITY'
PROTOCOL = 'official_a2a_sdk_ASGITransport'


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


class Trial:
    def __init__(self, cfg, spec, trial_id, stream):
        self.cfg, self.spec, self.trial_id, self.stream = cfg, spec, trial_id, stream
        self.events = []
        self.queue = asyncio.Queue()
        self.plane = TrustedPlane(cfg, self.emit, spec.get('ablation', []))
        self.hosts = {'agent-A': StageHost(self.plane, 'agent-A', ('memory', 'gateway', 'adapter')),
                      'agent-B': StageHost(self.plane, 'agent-B', ('adapter',))}
        self.materials, self.held = {}, {}
        self.adapter_errors, self.tampered, self.protocol_messages = 0, False, 0
        self.ops = {('agent-A', 'delegate'): self.a_delegate, ('agent-A', 'attempt'): self.a_attempt,
                    ('agent-B', 'execute'): self.b_execute, ('agent-B', 'prepare'): self.b_prepare,
                    ('agent-B', 'commit'): self.b_commit}
        self.agents = {
            name: OfficialA2AFunctionAgent(
                agent={'agent_id': name, 'name': name, 'capabilities': ['r2-continuity-delegation']},
                handler=lambda payload, agent_id=name: self.handle(agent_id, payload))
            for name in ('agent-A', 'agent-B')}

    # ---------------- evidence log ----------------
    def emit(self, event_type, source, **fields):
        event = dict(seq=len(self.events) + 1, timestamp_utc=utc(), trial_id=self.trial_id,
                     condition_id=self.spec['id'], scenario=self.spec['family'], group=self.spec['group'],
                     classification=CLASSIFICATION, event_type=event_type, source=source)
        event.update(fields)
        self.events.append(event)
        self.stream.write(json.dumps(event, ensure_ascii=False) + '\n')
        self.stream.flush()
        return event

    # ---------------- agent side (UNTRUSTED logic, scripted) ----------------
    def handle(self, agent_id, payload):
        operation = payload.get('operation')
        self.emit('agent_received', agent_id, operation=operation, work_id=payload.get('work_id'),
                  protocol_backend=PROTOCOL)
        action = self.ops.get((agent_id, operation))
        if action is None:
            return {'status': 'denied', 'reason': 'ADAPTER_UNKNOWN_OPERATION'}
        try:
            return action(agent_id, payload)
        except codec.ProofCodecError as error:  # malformed evidence is never repaired: fail closed
            self.emit('proof_rejected', agent_id, operation=operation, reason=str(error)[:300])
            return {'status': 'denied', 'reason': 'ADAPTER_MALFORMED_PROOF'}
        except Exception as error:  # noqa: BLE001 - surfaced as an adapter error, never as a pass
            self.adapter_errors += 1
            self.emit('adapter_exception', agent_id, operation=operation, error=f'{type(error).__name__}: {error}')
            return {'status': 'adapter_error'}

    def forward(self, agent_id, payload, bundle):
        work_id = payload['work_id']
        self.emit('delegation_requested', agent_id, work_id=work_id, destination_agent='agent-B',
                  bundle_digest=digest(bundle), receipts=len(bundle.receipts))
        self.queue.put_nowait(dict(destination='agent-B', operation=payload['next_operation'],
                                   work_id=work_id, bundle=codec.to_wire(bundle)))
        self.emit('queue_enqueued', agent_id, work_id=work_id, destination_agent='agent-B',
                  queue_size=self.queue.qsize(), reason='queue_acceptance_is_not_effect_finality')

    def a_delegate(self, agent_id, payload):
        host = self.hosts[agent_id]
        bundle = codec.from_wire(ProofBundle, payload['bundle'])
        bundle = host.apply(host.apply(bundle, 'memory'), 'gateway')
        self.forward(agent_id, payload, bundle)
        return {'status': 'queued', 'work_id': payload['work_id']}

    def a_attempt(self, agent_id, payload):
        host = self.hosts[agent_id]
        script = payload.get('a_script', {})
        bundle = codec.from_wire(ProofBundle, payload['bundle'])
        partial = host.apply(host.apply(bundle, 'memory'), 'gateway')
        bundle = host.apply(partial, 'adapter')
        decision, permit = self.plane.request_permit(bundle, agent_id)
        then = script.get('then', 'stop')
        result = {'status': 'completed', 'allowed': bool(decision and decision.allowed)}
        if then == 'dispatch_if_permit' and permit is not None:
            ok, reason, _ = self.plane.dispatch(agent_id, bundle.envelopes[-1].action, permit)
            result.update(dispatch_ok=ok, dispatch_reason=reason)
        if then == 'forward':
            self.emit('post_decision_continuation', agent_id, work_id=payload['work_id'],
                      prior_decision_allowed=result['allowed'],
                      reason='scripted_adversarial_forward_even_after_denial')
            self.forward(agent_id, payload, partial)
        return result

    def b_prepare_bundle(self, agent_id, payload):
        host = self.hosts[agent_id]
        bundle = codec.from_wire(ProofBundle, payload['bundle'])
        script = payload.get('b_script', {'mode': 'honest'})
        if script['mode'] == 'strip_proof':
            return adversary.strip_proof(bundle), script
        return host.apply(bundle, 'adapter'), script

    @staticmethod
    def final_action(bundle):
        return bundle.envelopes[-1].action if bundle.envelopes else None

    def b_execute(self, agent_id, payload):
        bundle, script = self.b_prepare_bundle(agent_id, payload)
        mode, action, result = script['mode'], self.final_action(bundle), {'status': 'completed'}
        if mode == 'ladder':
            return self.run_ladder(agent_id, bundle, action, script)
        if mode == 'skip_permit':
            ok, reason, _ = self.plane.dispatch(agent_id, action, None)
            return dict(result, dispatch_ok=ok, dispatch_reason=reason)
        decision, permit = self.plane.request_permit(bundle, agent_id)
        result['allowed'] = bool(decision and decision.allowed)
        if permit is not None:
            if mode == 'substitute_after_permit':
                action = adversary.substitute_action(action, script['substitution'])
            ok, reason, _ = self.plane.dispatch(agent_id, action, permit)
            result.update(dispatch_ok=ok, dispatch_reason=reason)
        return result

    def b_prepare(self, agent_id, payload):
        bundle, script = self.b_prepare_bundle(agent_id, payload)
        decision, permit = self.plane.request_permit(bundle, agent_id)
        self.held[payload['work_id']] = (permit, self.final_action(bundle))
        return {'status': 'completed', 'allowed': bool(decision and decision.allowed),
                'permit_held': permit is not None}

    def b_commit(self, agent_id, payload):
        permit, action = self.held.pop(payload['work_id'], (None, None))
        if permit is None:
            return {'status': 'completed', 'dispatch': 'NO_HELD_PERMIT'}
        ok, reason, _ = self.plane.dispatch(agent_id, action, permit)
        return {'status': 'completed', 'dispatch_ok': ok, 'dispatch_reason': reason}

    def run_ladder(self, agent_id, bundle, action, script):
        """Scripted attacker steps in order; stops at the first executed effect if asked."""
        public, host, obtained, executed = self.plane.public_info(), self.hosts[agent_id], None, False
        for step in script['ladder']:
            ok = None
            if step == 'request_permit':
                _, obtained = self.plane.request_permit(bundle, agent_id)
            elif step == 'dispatch_no_permit':
                ok, _, _ = self.plane.dispatch(agent_id, action, None)
            elif step == 'dispatch_forged_permit_own_signer':
                forged = adversary.forge_permit(bundle, action, host.held_signer('adapter'), public['sink_id'])
                ok, _, _ = self.plane.dispatch(agent_id, action, forged)
            elif step == 'dispatch_forged_permit_claimed_trusted_signer':
                forged = adversary.forge_permit(bundle, action, host.held_signer('adapter'), public['sink_id'],
                                                claimed_signer_id=public['trusted_permit_signer_id'])
                ok, _, _ = self.plane.dispatch(agent_id, action, forged)
            else:
                raise ValueError(f'unknown ladder step {step}')
            self.emit('adversary_step', agent_id, step=step)
            executed = executed or bool(ok)
            if executed and script.get('stop_on_effect'):
                break
        if obtained is not None and not executed:  # the attacker uses any permit it actually obtained
            self.plane.dispatch(agent_id, action, obtained)
        return {'status': 'completed', 'effect_reported_by_gateway': executed}

    # ---------------- harness (user, scheduler, untrusted queue) ----------------
    async def send(self, agent_id, operation, **payload):
        self.emit('a2a_request', 'harness', agent_id=agent_id, operation=operation,
                  work_id=payload.get('work_id'), protocol_backend=PROTOCOL)
        response = await self.agents[agent_id].send_data(dict(operation=operation, **payload))
        self.protocol_messages += 1
        self.emit('a2a_response', 'harness', agent_id=agent_id, operation=operation,
                  work_id=payload.get('work_id'), protocol_backend=PROTOCOL,
                  agent_card_name=response.agent_card['name'],
                  agent_card_path='/.well-known/agent-card.json', response=response.response)
        return response.response

    async def send_a(self, operation, label, next_operation='execute', **extra):
        bundle, _ = self.materials[label]
        await self.send('agent-A', operation, work_id=f'{self.trial_id}-work-{label}',
                        bundle=codec.to_wire(bundle), next_operation=next_operation, **extra)

    async def drain(self):
        while not self.queue.empty():
            entry = self.queue.get_nowait()
            tamper = self.spec.get('queue_tamper')
            if tamper and not self.tampered:  # the queue is untrusted storage
                before, entry['bundle'] = entry['bundle'], adversary.tamper_wire(entry['bundle'], tamper)
                self.tampered = True
                self.emit('queue_tampered', 'untrusted-queue', work_id=entry['work_id'], tamper=tamper,
                          before_sha256=sha256_text(before), after_sha256=sha256_text(entry['bundle']))
            self.emit('queue_dequeued', 'harness', work_id=entry['work_id'],
                      destination_agent=entry['destination'], queue_size=self.queue.qsize())
            await self.send(entry['destination'], entry['operation'], work_id=entry['work_id'],
                            bundle=entry['bundle'], b_script=self.spec.get('b_script', {'mode': 'honest'}))
            self.queue.task_done()

    def revoke(self, label):
        bundle, _ = self.materials[label]
        self.plane.revoke(bundle.root_grant.task_root)

    async def run(self):
        spec, family = self.spec, self.spec['family']
        self.emit('trial_started', 'harness', configuration=spec, group=spec['group'],
                  ablation=spec.get('ablation', []), trusted_permit_signer=self.plane.public_info()['trusted_permit_signer_id'],
                  policy_epoch=self.cfg['policy_epoch'], sink_id=self.plane.sink_id,
                  agent_identities={k: v['identity'] for k, v in self.cfg['agents'].items()},
                  oracle_semantics='IMMEDIATE_CUT_AT_FINALITY', original_sha=self.cfg['original_method']['pinned_sha'],
                  scheduler='deterministic_sequential_queue_schedule; no races')
        for material in spec['materials']:  # all roots are issued at trial start (as R1 did)
            self.materials[material['label']] = self.plane.issue_material(material, material['label'])
        a_script = spec.get('a_script', {})
        if family == 'delegated_normal':
            await self.send_a('delegate', 'rootA')
            await self.drain()
        elif family == 'direct_attempt':
            await self.send_a('attempt', 'rootA', a_script=a_script)
        elif family == 'deny_then_delegate':
            await self.send_a('attempt', 'rootA', a_script=a_script)
            await self.drain()
        elif family == 'stale_permit':
            await self.send_a('delegate', 'rootA', next_operation='prepare')
            await self.drain()  # B hosts the adapter stage and obtains (holds) a permit
            self.revoke('rootA')
            await self.send('agent-B', 'commit', work_id=f'{self.trial_id}-work-rootA')
        elif family == 'queued_then_cut':
            await self.send_a('delegate', 'rootA')
            self.revoke('rootA')
            await self.drain()
        elif family == 'independent_root':
            await self.send_a('delegate', 'rootA')
            self.revoke('rootA')
            await self.drain()
            await self.send_a('delegate', 'rootB')
            await self.drain()
        elif family == 'cut_then_create':
            self.revoke('rootA')
            await self.send_a('delegate', 'rootA')
            await self.drain()
        elif family == 'cut_then_direct':
            self.revoke('rootA')
            await self.send_a('attempt', 'rootA', a_script=a_script)
        else:
            raise ValueError(f'unknown family {family}')
        counts = Counter(e['event_type'] for e in self.events)
        verifier = [dict(by=e['requester'], allowed=e['allowed'], reason_codes=e['reason_codes'])
                    for e in self.events if e['event_type'] == 'verify_decision']
        attempts = [dict(caller=e['caller_agent'], ok=e['result_ok'], reason=e['result_reason'])
                    for e in self.events if e['event_type'] == 'finality_attempt']
        out = dict(trial_id=self.trial_id, condition_id=spec['id'], group=spec['group'], family=family,
                   event_count=len(self.events) + 1, observed_event_counts=dict(counts),
                   observed_verifier_decisions=verifier, observed_finality_attempts=attempts,
                   world_effect_count=len(self.plane.world.effects), adapter_errors=self.adapter_errors,
                   a2a_messages=self.protocol_messages, classification=CLASSIFICATION,
                   oracle_result='NOT_OBSERVED', model_calls=0)
        self.emit('trial_completed', 'harness', observed_summary=out,
                  reason='observed_counts_only; independent oracle and expectation check are separate programs')
        return out

    async def close(self):
        for agent in self.agents.values():
            await agent.aclose()


async def run_all(cfg, output_dir):
    summaries, worlds = [], {}
    with (output_dir / 'events.jsonl').open('x') as stream:
        for spec in cfg['conditions']:
            trial = Trial(cfg, spec, f'{spec["id"]}-r1', stream)
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
        raise RuntimeError('R2 forbids network socket connect (in-process ASGI transport only)')
    socket.socket.connect = no_socket_connect
    socket.create_connection = no_socket_connect

    summaries, worlds = asyncio.run(run_all(cfg, args.output_dir))
    summary = dict(classification=CLASSIFICATION, fixture='official_A2A_SDK_inprocess_transport_plus_original_CONTINUITY',
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
        uncommitted_code_paths=git_out('status', '--porcelain', '--', 'experiments/r2', 'scripts').splitlines(),
        code_sha256={p: sha(HERE / p) for p in ('scenario.py', 'trusted.py', 'adversary.py', 'proof_codec.py')},
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
