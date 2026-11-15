"""Reference models: independent re-implementations of the papers' DEFINITIONS (stdlib only).

REFERENCE_MODEL_FROM_PAPER_DEFINITION. These are NOT the papers' artifacts and they
do not measure any system. They compute, on the small graphs fixed in config.json,
what each paper's stated semantics says the answer is, so that coverage claims in
docs/R3_PRIOR_ART_COMPARISON.md are checkable. A model returns NOT_EXPRESSIBLE or
{'expressible': False} when the paper's model cannot state the question; it never
guesses an answer. Fidelity: DEFINITION_LEVEL (reading of the quoted statements).

Sources (quote ids in results/r3/research-provenance.json)
  VERA                     VERA-1, VERA-2, VERA-8; Def. 3/4 [summary]
  Authorization Revocation REV-1, REV-2, REV-4, REV-7, REV-9
  ResidualAuth             RES-1, RES-2, RES-5, RES-6
  Authorization Succession SUC-1, SUC-6, SUC-7
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABEL = 'REFERENCE_MODEL_FROM_PAPER_DEFINITION'


def reach(roots, edges, removed=frozenset()):
    seen, stack = set(roots), list(roots)
    while stack:
        node = stack.pop()
        for edge_id, (parent, child) in edges.items():
            if edge_id not in removed and parent == node and child not in seen:
                seen.add(child)
                stack.append(child)
    return seen


def incoming(edges, node):
    return sorted(e for e, (_, c) in edges.items() if c == node)


# ---- VERA: disjunctive authority over a signed multi-parent DAG ----
def vera(graph):
    roots, edges, target = graph['roots'], {k: tuple(v) for k, v in graph['edges'].items()}, graph['target']
    if graph['conjunctive_roots']:
        removed = frozenset(graph['revocations']['edge_e2'])
        or_active = target in reach(roots, edges, removed)
        and_authorized = all(target in reach([r], edges, removed) for r in graph['conjunctive_roots'])
        return {'expressible': False, 'or_semantics_C_active_after_edge_e2': or_active,
                'and_policy_violated_by_or_semantics': or_active and not and_authorized}
    out = {}
    for name, removed in graph['revocations'].items():
        removed = frozenset(removed)
        out[f'target_{name}'] = sorted(reach(roots, edges) - reach(roots, edges, removed))   # Def. 4
        out[f'C_active_after_{name}'] = target in reach(roots, edges, removed)
    return out


# ---- ResidualAuth: cascading effectiveness along ONE selected parent per grant ----
def residualauth(graph):
    roots, edges, target = graph['roots'], {k: tuple(v) for k, v in graph['edges'].items()}, graph['target']
    if graph['conjunctive_roots']:
        return {'expressible': 'NOT_FOUND'}

    def selected_parent(edge_id):
        issuer = edges[edge_id][0]
        return None if issuer in roots else incoming(edges, issuer)[0]

    def effective(edge_id, revoked):
        if edge_id in revoked:
            return False
        parent = selected_parent(edge_id)
        return True if parent is None else effective(parent, revoked)

    into_target = incoming(edges, target)
    out = {}
    for name, removed in graph['revocations'].items():
        removed = frozenset(removed)
        graph_effective = any(effective(e, removed) for e in into_target)
        out[('graph_' if len(into_target) > 1 else '') + f'C_effective_after_{name}'] = graph_effective
        if len(into_target) > 1 and name == 'root_edge_e1':
            for edge_id in into_target:  # a record bound to ONE selected parent (RES-1, RES-6)
                out[f'ledger_selected_parent_{edge_id}_after_{name}'] = effective(edge_id, removed)
    return out


# ---- Authorization Succession: single-parent lineage atoms, ancestor cut ----
def succession(graph):
    roots, edges, target = graph['roots'], {k: tuple(v) for k, v in graph['edges'].items()}, graph['target']
    if graph['conjunctive_roots'] or any(len(incoming(edges, n)) > 1 for n in {c for _, c in edges.values()}):
        return {'expressible': False}                      # multi-parent merge is excluded (SUC-1, SUC-2)

    def lineage(node):
        atoms = {node}
        while incoming(edges, node):
            node = edges[incoming(edges, node)[0]][0]
            atoms.add(node)
        return atoms

    out = {}
    for name, removed in graph['revocations'].items():
        cut = {edges[e][1] for e in removed}               # in a tree, cutting an edge = cutting its child's atom
        out[f'C_current_after_{name}'] = not (lineage(target) & cut)
    return out


# ---- Authorization Revocation: antichain of conjunctive witnesses over ROOT atoms ----
def revocation(graph):
    roots, edges, target = graph['roots'], {k: tuple(v) for k, v in graph['edges'].items()}, graph['target']
    if graph['conjunctive_roots']:
        support = [frozenset(graph['conjunctive_roots'])]
    else:
        support = [frozenset([r]) for r in sorted(roots) if target in reach([r], edges)]
    retired = {edges[graph['revocations']['root_edge_e1'][0]][0]}   # root cut of the root at the tail of e1
    current = set(roots) - retired
    authorized = any(w <= current for w in support)
    out = {'C_authorized_after_edge_e2': 'NOT_EXPRESSIBLE',            # an intermediate edge is not an atom (REV-9)
           'C_authorized_after_root_edge_e1': authorized}
    if len(support) > 1:
        out['rebind_to_independent_support'] = any(not (w & retired) and w <= current for w in support)
    if graph['conjunctive_roots']:
        out['strict_subset_can_authorize'] = any(w <= current for w in support if len(w) < len(support[0]))
    return out


MODELS = {'VERA': vera, 'ResidualAuth': residualauth, 'Succession': succession, 'Revocation': revocation}


def compute(config):
    return {gid: {name: fn(graph) for name, fn in MODELS.items()} for gid, graph in config['reference_graphs'].items()}


def compare(expected, computed):
    mismatches = []
    for gid, models in expected.items():
        if gid == 'note':
            continue
        for model, keys in models.items():
            got = computed.get(gid, {}).get(model)
            if got != keys:
                mismatches.append(dict(graph=gid, model=model, expected=keys, computed=got))
    return mismatches


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--config', type=Path, default=HERE / 'config.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('preserve existing evidence; choose a new output')
    config = json.loads(args.config.read_text())
    computed = compute(config)
    mismatches = compare(config['reference_model_expected'], computed)
    out = dict(classification=LABEL, fidelity='DEFINITION_LEVEL; not original artifacts; not a measurement of any system',
               graphs=config['reference_graphs'], computed=computed,
               matches_preregistered_expectation=not mismatches, mismatches=mismatches)
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'label': LABEL, 'matches_preregistered_expectation': not mismatches,
                      'mismatch_count': len(mismatches)}))
    return 0 if not mismatches else 1


if __name__ == '__main__':
    sys.exit(main())
