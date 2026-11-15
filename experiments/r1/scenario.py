"""R1 deterministic intervention-boundary fixture; not a paper reproduction.

Original Progent wrapper dispatches an in-memory sink. Original A2ASecBench
OfficialA2AFunctionAgent supplies official-SDK ASGI messages, not its benchmark
cases/scorer. Scheduling, authority ledger and sink fence are testbed controls.
"""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
import copy
import datetime as dt
import hashlib
import importlib.metadata
import json
from pathlib import Path
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'third_party/a2asecbench'))
from harness.a2a_lab.sdk_protocol import OfficialA2AFunctionAgent
from secagent import apply_secure_tool_wrapper, update_security_policy
from secagent.tool import ValidationError

NOT = 'NOT_OBSERVED'


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


class Trial:
    def __init__(self, spec, trial_id, stream):
        self.spec, self.trial_id, self.stream = spec, trial_id, stream
        self.events, self.grants, self.cuts, self.fences = [], {}, {}, {}
        self.queue = asyncio.Queue()
        self.receipts, self.commits = {}, []
        self.context = None
        self.policy_revision = 0
        self.current_policy_version = NOT
        self.active_agents = set()
        self.protocol_messages = 0
        self.work_counter = 0

        def protected_send(work_id: str, root_task_id: str, principal_id: str,
                           authorization_support: str, recipient: str, body: str) -> str:
            """Accept a synthetic message in the in-memory receipt store."""
            work, agent_id, enforced, immediate_commit = self.context
            self.emit('policy_decision', work, agent_id=agent_id,
                      policy_decision='allow' if enforced else 'NOT_APPLIED',
                      reason=('original_wrapper_dispatched_callable' if enforced
                              else 'deliberately_unmediated_baseline'),
                      decision_observation='protected callable entry after original wrapper check'
                      if enforced else 'no original wrapper invoked')
            if root_task_id in self.fences:
                self.emit('sink_reject', work, agent_id=agent_id,
                          reason='root_sink_fence_active', committed_effect=False)
                return 'REJECTED_BY_SINK_FENCE'
            receipt_id = f'{self.trial_id}-receipt-{len(self.receipts)+1}'
            acceptance = self.emit('sink_accept', work, agent_id=agent_id,
                                   receipt_id=receipt_id,
                                   accepted_at=self.next_seq, accepted_at_seq=self.next_seq,
                                   accepted_at_utc=utc(), reason='in_memory_receipt_created')
            self.receipts[receipt_id] = dict(work=copy.deepcopy(work),
                accepted_at=acceptance['seq'], accepted_at_utc=acceptance['timestamp_utc'],
                cancelled=False, committed=False, agent_id=agent_id)
            if immediate_commit:
                self.commit(receipt_id)
            return receipt_id

        self.raw_tool = protected_send
        self.guarded_tool = apply_secure_tool_wrapper(protected_send)
        self.agents = {
            name: OfficialA2AFunctionAgent(agent={
                'agent_id': name, 'name': name, 'capabilities': ['r1-synthetic-dispatch'],
            }, handler=lambda payload, agent_id=name: self.handle(agent_id, payload))
            for name in ('agent-A', 'agent-B')
        }

    @property
    def next_seq(self):
        return len(self.events)+1

    def emit(self, event_type, work=None, **fields):
        event = dict(seq=self.next_seq, timestamp_utc=utc(), trial_id=self.trial_id,
                     scenario=self.spec['scenario'], condition_id=self.spec['id'],
                     classification='SYNTHETIC_MULTI_AGENT_EXPERIMENT',
                     event_type=event_type, work_id=NOT, root_task_id=NOT,
                     principal_id=NOT, agent_id=NOT, delegation_parent=NOT,
                     input_provenance=NOT, authorization_support=NOT,
                     proposed_tool_call=NOT, args=NOT, policy_version=self.current_policy_version,
                     policy_decision=NOT, reason=NOT, authorization_cut=NOT, fence=NOT,
                     accepted_at=NOT, committed_at=NOT, committed_effect=NOT,
                     benign_task_success=NOT, oracle_result=NOT)
        if work is not None:
            for key in ('work_id','root_task_id','principal_id','delegation_parent',
                        'input_provenance','authorization_support'):
                event[key] = copy.deepcopy(work.get(key, NOT))
            event['proposed_tool_call'] = 'protected_send'
            event['args'] = self.arguments(work)
        event.update(fields)
        root = event['root_task_id']
        if root in self.cuts:
            event['authorization_cut'] = self.cuts[root]
        if root in self.fences:
            event['fence'] = self.fences[root]
        self.events.append(event)
        self.stream.write(json.dumps(event, ensure_ascii=False)+'\n')
        self.stream.flush()
        return event

    @staticmethod
    def arguments(work):
        return {key:work[key] for key in ('work_id','root_task_id','principal_id',
                                         'authorization_support','recipient','body')}

    def grant(self, root, principal, support, recipient):
        grant = dict(support_id=support, root_task_id=root, principal_id=principal,
                     tool='protected_send', recipient=recipient)
        self.grants[support] = dict(grant, active=True)
        self.emit('grant', root_task_id=root, principal_id=principal,
                  authorization_support=support, grant=grant,
                  reason='trusted_fixture_root_authorization')

    def revoke(self, root):
        cut = dict(seq=self.next_seq, timestamp_utc=utc())
        self.cuts[root] = cut
        for grant in self.grants.values():
            if grant['root_task_id'] == root:
                grant['active'] = False
        self.emit('revoke', root_task_id=root, authorization_cut=cut,
                  reason='fixture_root_scoped_authority_cut')
        if self.spec.get('sink_fence', False):
            fence = dict(seq=self.next_seq, timestamp_utc=utc(), mode='cancel_pending')
            self.fences[root] = fence
            self.emit('sink_fence', root_task_id=root, fence=fence,
                      reason='testbed_control_cancel_pending_and_reject_new_acceptance')
            for receipt_id, receipt in self.receipts.items():
                if receipt['work']['root_task_id'] == root and not receipt['committed']:
                    receipt['cancelled'] = True
                    self.emit('sink_cancel', receipt['work'], receipt_id=receipt_id,
                              accepted_at=receipt['accepted_at'], committed_effect=False,
                              reason='pending_receipt_cancelled_by_root_sink_fence')

    def policy(self, active_only):
        rules = []
        for grant in self.grants.values():
            if active_only and not grant['active']:
                continue
            condition = {key:{'enum':[grant[key]]} for key in ('root_task_id','principal_id','recipient')}
            condition['authorization_support'] = {'enum':[grant['support_id']]}
            rules.append((1,0,condition,0))
        # Explicit forbid rule makes the empty-active-authority case well-defined.
        rules.append((99,1,{},0))
        return {'protected_send':rules}

    def configure_policy(self):
        view = self.spec['authority_view']
        self.policy_revision += 1
        if view == 'static':
            policy = copy.deepcopy(self.initial_policy)
        elif view == 'global_stop' and self.cuts:
            policy = {'protected_send':[(1,1,{},0)]}
        else:
            policy = self.policy(active_only=True)
        self.current_policy_version = f'{self.spec["id"]}:{view}:v{self.policy_revision}'
        update_security_policy(policy)
        self.emit('policy_loaded', policy_definition=policy, authority_view=view,
                  reason='original_update_security_policy_called')

    def make_work(self, root='root-A', recipient=None):
        self.work_counter += 1
        grant = self.grants['support-A' if root == 'root-A' else 'support-B']
        return dict(work_id=f'{self.trial_id}-work-{self.work_counter}',
                    root_task_id=root, principal_id=grant['principal_id'],
                    authorization_support=grant['support_id'],
                    delegation_parent=NOT,
                    input_provenance=['trusted_fixture_task',
                       'untrusted_fixture_recipient_substitution' if recipient else 'synthetic_report'],
                    recipient=recipient or grant['recipient'], body='synthetic-r1-report')

    def execute(self, work, agent_id, immediate_commit=True):
        scope = self.spec['mediation']
        enforced = scope == 'all' or (scope == 'A_only' and agent_id == 'agent-A')
        if enforced:
            self.configure_policy()
        else:
            self.current_policy_version = 'NOT_APPLIED'
        self.emit('policy_proposed', work, agent_id=agent_id,
                  mediation_applied=enforced, authority_view=self.spec['authority_view'],
                  immediate_commit=immediate_commit)
        self.context = work,agent_id,enforced,immediate_commit
        try:
            receipt = (self.guarded_tool if enforced else self.raw_tool)(**self.arguments(work))
            return dict(receipt_id=receipt, dispatch='returned')
        except ValidationError as error:
            self.emit('policy_decision', work, agent_id=agent_id, policy_decision='deny',
                      reason=str(error), committed_effect=False,
                      decision_observation='original_Progent_ValidationError')
            return dict(receipt_id=NOT, dispatch='denied')
        finally:
            self.context = None

    def commit(self, receipt_id):
        receipt = self.receipts[receipt_id]
        if receipt['cancelled']:
            self.emit('commit_attempt_cancelled', receipt['work'], receipt_id=receipt_id,
                      accepted_at=receipt['accepted_at'], committed_effect=False,
                      reason='cancelled_receipt_has_no_effect')
            return
        if receipt['committed']:
            raise RuntimeError('duplicate fixture commit')
        receipt['committed'] = True
        effect = dict(receipt_id=receipt_id, root_task_id=receipt['work']['root_task_id'],
                      principal_id=receipt['work']['principal_id'],
                      recipient=receipt['work']['recipient'], body=receipt['work']['body'])
        self.commits.append(effect)
        self.emit('sink_commit', receipt['work'], agent_id=receipt['agent_id'],
                  receipt_id=receipt_id, accepted_at=receipt['accepted_at'],
                  accepted_at_seq=receipt['accepted_at'], committed_at=self.next_seq,
                  committed_at_seq=self.next_seq, committed_effect=effect,
                  reason='in_memory_outbox_append')

    def handle(self, agent_id, payload):
        self.active_agents.add(agent_id)
        work = copy.deepcopy(payload['work'])
        op = payload['operation']
        self.emit('agent_received', work, agent_id=agent_id, operation=op,
                  protocol_backend='official_a2a_sdk_ASGITransport')
        if op in ('create_queue','direct','deny_then_queue'):
            self.emit('message_created', work, agent_id=agent_id,
                      reason='deterministic_fixture_message_generation')
        if op in ('direct','deny_then_queue','execute'):
            result = self.execute(work, agent_id, payload.get('immediate_commit',True))
            if op != 'deny_then_queue':
                return result
            # Deliberately adversarial fixture behavior, not a recovery decision by an LLM.
            self.emit('post_decision_continuation', work, agent_id=agent_id,
                      prior_dispatch=result['dispatch'],
                      reason='scripted_adversarial_forward_even_after_denial')
        destination = payload.get('destination','agent-B')
        work['delegation_parent'] = agent_id
        self.emit('delegation_requested', work, agent_id=agent_id, destination_agent=destination)
        self.queue.put_nowait(dict(destination=destination,work=work,
                                  immediate_commit=payload.get('immediate_commit',True)))
        self.emit('queue_enqueued', work, agent_id=agent_id, destination_agent=destination,
                  queue_size=self.queue.qsize(),
                  reason='queue_acceptance_is_not_protected_sink_acceptance')
        return dict(queued=True,work_id=work['work_id'])

    async def send(self, agent_id, operation, work, **options):
        self.emit('a2a_request',work,agent_id=agent_id,operation=operation,
                  protocol_backend='official_a2a_sdk_ASGITransport')
        response = await self.agents[agent_id].send_data(dict(operation=operation,work=work,**options))
        self.protocol_messages += 1
        self.emit('a2a_response',work,agent_id=agent_id,operation=operation,
                  protocol_backend='official_a2a_sdk_ASGITransport',
                  agent_card_name=response.agent_card['name'],
                  agent_card_path='/.well-known/agent-card.json',response=response.response)
        return response.response

    async def drain(self):
        last = None
        while not self.queue.empty():
            entry = self.queue.get_nowait()
            self.emit('queue_dequeued',entry['work'],agent_id=entry['destination'],queue_size=self.queue.qsize())
            last = await self.send(entry['destination'],'execute',entry['work'],
                                   immediate_commit=entry['immediate_commit'])
            self.queue.task_done()
        return last

    async def run(self):
        self.emit('trial_started', configuration=self.spec,
                  authority_semantics='current_root_principal_support_at_sink_acceptance',
                  oracle_semantics='IMMEDIATE_CUT_AT_ACCEPT; separate post-fence-admission lens required',
                  commit_semantics='cancel_pending_fence' if self.spec.get('sink_fence') else 'grandfather_preaccepted_receipts',
                  scheduler='deterministic_sequential_queue_schedule; no races')
        self.grant('root-A','principal-A','support-A','owner-A@example.test')
        self.grant('root-B','principal-B','support-B','owner-B@example.test')
        self.initial_policy = self.policy(active_only=True)
        family = self.spec['schedule']
        work = None if family in ('cut_create_dispatch','cut_create_direct') else self.make_work(
            recipient='attacker@example.test' if self.spec.get('unauthorized') else None)
        if family == 'normal_queue':
            await self.send('agent-A','create_queue',work)
            await self.drain()
        elif family == 'direct':
            await self.send('agent-A','direct',work)
        elif family == 'deny_then_queue':
            await self.send('agent-A','deny_then_queue',work,
                            destination=self.spec.get('destination','agent-B'))
            await self.drain()
        elif family == 'prequeue_cut_dispatch':
            await self.send('agent-A','create_queue',work)
            self.revoke('root-A')
            await self.drain()
        elif family == 'cut_create_dispatch':
            self.revoke('root-A')
            work = self.make_work()
            await self.send('agent-A','create_queue',work)
            await self.drain()
        elif family == 'cut_create_direct':
            self.revoke('root-A')
            work = self.make_work()
            await self.send('agent-A','direct',work)
        elif family == 'preaccept_cut_commit':
            await self.send('agent-A','create_queue',work,immediate_commit=False)
            response = await self.drain()
            self.revoke('root-A')
            if response['receipt_id'] in self.receipts:
                self.commit(response['receipt_id'])
        elif family == 'independent_root':
            await self.send('agent-A','create_queue',work)
            self.revoke('root-A')
            await self.drain()
            independent = self.make_work(root='root-B')
            await self.send('agent-A','create_queue',independent)
            await self.drain()
        else:
            raise ValueError(f'Unknown schedule: {family}')
        counts = Counter(e['event_type'] for e in self.events)
        decisions = Counter(e['policy_decision'] for e in self.events if e['event_type']=='policy_decision')
        out = dict(trial_id=self.trial_id,condition_id=self.spec['id'],scenario=self.spec['scenario'],
                   event_count=len(self.events),observed_event_counts=dict(counts),
                   observed_policy_decisions=dict(decisions),committed_effects=self.commits,
                   active_agents=sorted(self.active_agents),a2a_messages=self.protocol_messages,
                   classification='SYNTHETIC_MULTI_AGENT_EXPERIMENT',
                   oracle_result=NOT,model_calls=0)
        self.emit('trial_completed',observed_summary=out,
                  reason='observed_counts_only; independent oracle is a separate program')
        return out

    async def close(self):
        for agent in self.agents.values():
            await agent.aclose()


async def run_all(config,output_dir):
    summaries,sink_states=[],{}
    with (output_dir/'events.jsonl').open('x') as stream:
        for repeat in range(config.get('repetitions',1)):
            for spec in config['conditions']:
                trial=Trial(spec,f'{spec["id"]}-r{repeat+1}',stream)
                try:
                    summaries.append(await trial.run())
                    sink_states[trial.trial_id] = dict(
                        receipts=copy.deepcopy(trial.receipts),
                        outbox=copy.deepcopy(trial.commits))
                finally:
                    await trial.close()
    return summaries,sink_states


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--config',type=Path,default=Path(__file__).with_name('config.json'))
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    config=json.loads(args.config.read_text())
    # ASGI transport is in-process. No Internet or loopback sockets are required.
    def no_socket_connect(*args,**kwargs):
        raise RuntimeError('R1 fixture forbids network socket connect')
    socket.socket.connect=no_socket_connect
    socket.create_connection=no_socket_connect
    summaries,sink_states=asyncio.run(run_all(config,args.output_dir))
    summary=dict(classification='SYNTHETIC_MULTI_AGENT_EXPERIMENT',
                 fixture='official_A2A_SDK_inprocess_transport_plus_original_Progent_wrapper',
                 original_paper_reproduction=False,model_calls=0,
                 trial_count=len(summaries),trials=summaries)
    (args.output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.output_dir/'sink_state.json').write_text(json.dumps(sink_states,indent=2)+'\n')
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    versions={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    manifest=dict(created_utc=utc(),python=sys.version,package_versions=versions,
                  parent_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  code_sha256=sha(Path(__file__)),config_sha256=sha(args.config),
                  source_commits={name:subprocess.check_output(['git','-C',str(ROOT/'third_party'/name),'rev-parse','HEAD'],text=True).strip()
                                  for name in ('progent','a2asecbench')},
                  source_file_sha256={str(p.relative_to(ROOT)):sha(p) for p in
                      (ROOT/'third_party/progent/secagent/tool.py',ROOT/'third_party/a2asecbench/harness/a2a_lab/sdk_protocol.py')},
                  events_sha256=sha(args.output_dir/'events.jsonl'),
                  sink_state_sha256=sha(args.output_dir/'sink_state.json'),
                  summary_sha256=sha(args.output_dir/'summary.json'))
    (args.output_dir/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for trial in summaries:
        print(json.dumps({k:trial[k] for k in ('trial_id','observed_policy_decisions','active_agents','a2a_messages')},
                         ensure_ascii=False), 'commits='+str(len(trial['committed_effects'])))
    print(json.dumps({'trial_count':len(summaries),'event_file':str(args.output_dir/'events.jsonl'),
                      'oracle_result':'NOT_OBSERVED; run independent oracle separately'}))


if __name__=='__main__':
    main()
