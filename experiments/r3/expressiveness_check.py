"""Static expressiveness check of the ORIGINAL CONTINUITY (pre-registered S1-S7).

Question: can CONTINUITY's RootGrant model represent a parent or derived grant,
edge-level or lineage revocation, independent support or conjunctive approval?
This inspects structure only (dataclass fields, AST of core.py, function source).
No security decision is invoked on any scenario; the original is imported unmodified
after the pinned-SHA check in trusted.py. Run with the R2 environment.

Every check works on source TEXT or objects passed in, so tests can feed synthetic
sources and confirm that a violation would be detected (the checker is not vacuous).
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import hashlib
import inspect
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LINEAGE_FIELD = re.compile(r'parent|lineage|edge|deriv|ancestor|chain|origin', re.I)
LINEAGE_TOKEN = re.compile(r'\b(parents?|lineage|quorum|approvers?|edges?)\b', re.I)
ALLOWED_REVOKED_OPERANDS = {'grant.grant_id', 'release.release_id', 'context.root_grant_id',
                            'permit.grant_id', 'permit.permit_id'}
RUNTIME_STATE_FIELDS = {'policy_id', 'policy_digest', 'policy_epoch', 'revoked_ids'}


def field_names(cls):
    return [f.name for f in dataclasses.fields(cls)]


def s1_no_lineage_field(grant_cls):
    names = field_names(grant_cls)
    hits = [n for n in names if LINEAGE_FIELD.search(n)]
    return dict(id='S1', holds=not hits, observed=dict(root_grant_fields=names, lineage_like_fields=hits))


def s2_runtime_state_fields(state_cls):
    names = set(field_names(state_cls))
    return dict(id='S2', holds=names == RUNTIME_STATE_FIELDS, observed=dict(runtime_state_fields=sorted(names)))


def s3_revocation_operands(core_source):
    operands = []
    for node in ast.walk(ast.parse(core_source)):
        if (isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], (ast.In, ast.NotIn))
                and isinstance(node.comparators[0], ast.Attribute) and node.comparators[0].attr == 'revoked_ids'):
            operands.append(ast.unparse(node.left))
    holds = bool(operands) and set(operands) <= ALLOWED_REVOKED_OPERANDS
    return dict(id='S3', holds=holds, observed=dict(revoked_ids_membership_operands=sorted(operands),
                                                    allowed=sorted(ALLOWED_REVOKED_OPERANDS)))


def s4_approval_digest_unused(core_source):
    reads, fields, strings = [], 0, []
    for node in ast.walk(ast.parse(core_source)):
        if isinstance(node, ast.Attribute) and node.attr == 'approval_digest':
            reads.append(ast.unparse(node))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == 'approval_digest':
            fields += 1
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and 'approval_digest' in node.value:
            strings.append(node.value)
    holds = not reads and fields == 1 and strings == ['/context/approval_digest']
    return dict(id='S4', holds=holds, observed=dict(attribute_reads=reads, field_definitions=fields,
                                                    string_constants=strings))


def s5_parent_argument_rejected(grant):
    try:
        dataclasses.replace(grant, parent_grant_id='grant:other')
    except TypeError as error:
        return dict(id='S5', holds=True, observed=dict(raised='TypeError', message=str(error)[:120]))
    return dict(id='S5', holds=False, observed=dict(raised=None))


def s6_no_lineage_tokens(sources):
    hits = {name: sorted({m.group(0).lower() for m in LINEAGE_TOKEN.finditer(src)}) for name, src in sources.items()}
    hits = {k: v for k, v in hits.items() if v}
    return dict(id='S6', holds=not hits, observed=dict(inspected=sorted(sources), token_hits=hits))


def s7_delegation_scope_uses(core_source):
    tree = ast.parse(core_source)
    parent = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    uses, other = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == 'delegation_scope':
            up = parent.get(node)
            kind = 'other'
            if isinstance(up, ast.Attribute) and up.attr == 'issubset' and up.value is node:
                kind = 'subset'
            elif isinstance(up, ast.Call) and node in up.args and isinstance(up.func, ast.Attribute) and up.func.attr == 'issubset':
                kind = 'subset'
            elif isinstance(up, ast.Compare) and isinstance(up.ops[0], (ast.In, ast.NotIn)) and node in up.comparators:
                kind = 'membership'
            uses.append(kind)
            if kind == 'other':
                other.append(ast.unparse(up)[:100])
    constructor_calls = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
                            and isinstance(n.func, ast.Name) and n.func.id == 'RootGrant')
    holds = bool(uses) and not other and constructor_calls == 0
    return dict(id='S7', holds=holds, observed=dict(uses={k: uses.count(k) for k in set(uses)}, other_uses=other,
                                                    root_grant_constructor_calls_in_core=constructor_calls))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('preserve existing evidence; choose a new output')
    sys.path.insert(0, str(ROOT / 'experiments/r2'))
    import trusted  # noqa: F401  (verifies the pinned, unmodified original and sets sys.path)
    from continuity import core, experiment
    core_path = Path(core.__file__)
    core_source = core_path.read_text()
    grant = experiment.make_scenario('workspace', 1016, 'benign',
                                     infra=experiment.build_infrastructure()).root_grant
    entry_sources = {'ContinuityVerifier.verify_bundle': inspect.getsource(core.ContinuityVerifier.verify_bundle),
                     'FinalitySink.execute': inspect.getsource(core.FinalitySink.execute)}
    informational = {'ContinuityVerifier(class)': inspect.getsource(core.ContinuityVerifier),
                     'FinalitySink(class)': inspect.getsource(core.FinalitySink),
                     'EffectBroker(class)': inspect.getsource(core.EffectBroker)}
    checks = [s1_no_lineage_field(core.RootGrant), s2_runtime_state_fields(core.RuntimeState),
              s3_revocation_operands(core_source), s4_approval_digest_unused(core_source),
              s5_parent_argument_rejected(grant), s6_no_lineage_tokens(entry_sources),
              s7_delegation_scope_uses(core_source)]
    extra = s6_no_lineage_tokens(informational)
    out = dict(classification='STATIC_EXPRESSIVENESS_CHECK_OF_ORIGINAL_CONTINUITY',
               original_head=trusted.PINNED_SHA, core_sha256=hashlib.sha256(core_path.read_bytes()).hexdigest(),
               checks=checks, all_preregistered_predictions_hold=all(c['holds'] for c in checks),
               informational_not_preregistered=dict(whole_class_token_scan=extra),
               meaning=('If S1-S7 hold, a separately signed grant is an independent root for CONTINUITY: there is no parent '
                        'reference, no dependency semantics and no effect-time dependency check. This is a model scope '
                        'limit (SCOPE_EXTENSION / POLICY_MODEL_MISMATCH), not a defect.'))
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'all_preregistered_predictions_hold': out['all_preregistered_predictions_hold'],
                      **{c['id']: c['holds'] for c in checks}}))
    return 0 if out['all_preregistered_predictions_hold'] else 1


if __name__ == '__main__':
    sys.exit(main())
