"""Provenance of the prior-art evidence used in R3 (stdlib only).

Reads downloaded papers and a downloaded artifact strictly as DATA (run it with
`python3 -I`). Nothing downloaded is imported or executed. It records:
  * sha256 and size of each locally cached paper text,
  * whether every quote cited in the R3 documents occurs VERBATIM in that text
    (whitespace and typographic quotes normalised),
  * the downloaded VERA artifact's archive hash, per-file hashes and read-only
    static facts (no execution; see docs/R3_PRIOR_ART_COMPARISON.md section 4).
Paper texts are not committed (copyright); a reader with the same arXiv versions
can re-run this and compare the hashes/quote flags.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

PAPERS = {
    'continuity': dict(arxiv_id='2609.05269', version='v1', short='CONTINUITY',
                       title='CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls',
                       authors=['Chris Zheng', 'Geng Yang'], submitted='2026-09-04'),
    'vera': dict(arxiv_id='2608.30091', version='v1', short='VERA',
                 title='VERA: Authority-Preserving Edge Revocation for Federated AI-Agent Workflows',
                 authors=['Lifei Liu', 'Haoran Yu', 'Xiaochong Jiang'], submitted='2026-08-30'),
    'revocation': dict(arxiv_id='2609.21284', version='v1', short='Authorization Revocation',
                       title='Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution',
                       authors=['Genliang Zhu', 'Chu Wang'], submitted='2026-09-18'),
    'residualauth': dict(arxiv_id='2609.08062', version='v2', short='ResidualAuth',
                         title='ResidualAuth: What Authorization State Must Language Agents Preserve under Revocable Delegation?',
                         authors=['Moonwon Choi', 'Seokho Jeong', 'Sian Choi', 'Seunggeun Lee'],
                         submitted='2026-09-08 (v1), 2026-09-30 (v2)',
                         title_note='arXiv abstract page title says "Language Agents"; the v2 HTML text says "Agent Systems"'),
    'succession': dict(arxiv_id='2610.00347', version='v1', short='Authorization Succession',
                       title='Authorization for Self-Modifying AI Agent Populations: Conserving Authority across Replacement, Forking, and Rollback',
                       authors=['Genliang Zhu', 'Chu Wang'], submitted='2026-09-29'),
}

# (paper key, id, quote). Plain prose only, so the HTML->text conversion cannot mangle it.
QUOTES = [
    ('vera', 'VERA-1', 'It does not cover threshold approval or all-parent approval; those policies require different target functions.'),
    ('vera', 'VERA-2', 'A node with an alternate authorizing root path must stay active.'),
    ('vera', 'VERA-3', 'hot-path authorization uses cached verified revocation state'),
    ('vera', 'VERA-4', 'The artifact is available at'),
    ('vera', 'VERA-5', 'None directly provides a multi-parent, cross-domain edge target'),
    ('vera', 'VERA-6', 'the edge target preserves the shared agent in all 320 cases while tree cascade revokes it in all 320'),
    ('vera', 'VERA-7', 'APS is closest among agent proposals but uses a single-parent rooted tree'),
    ('revocation', 'REV-1', 'A carrier may have conjunctive requirements and alternative roots.'),
    ('revocation', 'REV-2', 'Treating its roots as a flat union would over-revoke independently authorized work; treating them as an existential set would permit root laundering.'),
    ('revocation', 'REV-3', 'It neither declares the whole system idle nor revokes work supported by other roots.'),
    ('revocation', 'REV-4', 'a strict subset of a conjunctive witness cannot authorize an effect'),
    ('revocation', 'REV-5', 'Registry and manifest completeness'),
    ('revocation', 'REV-6', 'Issuer mediation and non-expansion'),
    ('revocation', 'REV-7', 'Theorem 12 (Independent-support preservation)'),
    ('revocation', 'REV-8', 'Theorem 14 (Crash/replay stability and unrelated-root locality)'),
    ('revocation', 'REV-9', 'Exact delegation-edge revocation the authority consequences of removing a selected graph edge'),
    ('revocation', 'REV-10', 'The evaluated system is the executable durable-ledger artifact, its 17-case late-effect test suite, and the separately implemented checker.'),
    ('revocation', 'REV-11', 'represents alternative and conjunctive authority as antichains of minimal sufficient root sets'),
    ('succession', 'SUC-1', 'The core transition system admits no multi-parent child and no merge rule.'),
    ('succession', 'SUC-2', 'Multi-parent authority merge is outside the formal, implemented, and executed result.'),
    ('succession', 'SUC-3', 'such coordination does not create an authorization parent edge or union their grants'),
    ('succession', 'SUC-4', 'Executable artifacts, adapters, checker traces, temporary files, source caches, and non-manuscript research materials remain outside that archive.'),
    ('succession', 'SUC-5', 'Our protocol assumes such complete mediation'),
    ('succession', 'SUC-6', 'conserves authority across a single-parent generation forest'),
    ('residualauth', 'RES-1', 'an optional immutable selected parent'),
    ('residualauth', 'RES-2', 'Cascading effectiveness is the well-founded recursion'),
    ('residualauth', 'RES-3', 'A hard gate separately checks proposals against a trusted ledger before execution'),
    ('residualauth', 'RES-4', 'not an end-to-end replay of the experiment repository'),
    ('continuity', 'CON-1', 'Authority and delegation can increase only through a separately authenticated grant'),
    ('continuity', 'CON-2', 'only a verified grant edge may add authority'),
    ('continuity', 'CON-3', 'Key rotation, quorum authorization, hardware roots, and certificate-path validation are outside the prototype.'),
    ('continuity', 'CON-4', 'Complete mediation is an engineering and governance obligation.'),
    ('continuity', 'CON-5', 'A permit issued before a grant is revoked is rejected at finality.'),
    ('continuity', 'CON-6', 'The proof protects only sinks that require a valid permit.'),
    ('continuity', 'CON-7', 'A deployment must enumerate protected effect classes'),
    ('vera', 'VERA-8', 'Simultaneous revocations must yield the exact joint target, not necessarily the union of single-edge targets.'),
    ('revocation', 'REV-12', 'No descendant inherits the rebind merely from ancestry; it must either be covered by the same atomic profile transition or carry its own receipt.'),
    ('revocation', 'REV-13', 'obligations and carrier effects already emitted before or across the revocation cut'),
    ('succession', 'SUC-7', 'Ancestor cuts invalidate dependent descendants; rollback creates a fresh generation without restoring spent authority; a new root requires an independent grant.'),
    ('residualauth', 'RES-5', 'an idempotent grant never reparents an authorized target'),
    ('residualauth', 'RES-6', 'One parent per record does not mean one incoming grant per principal.'),
]


def norm(text):
    text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', text)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--artifact-zip', type=Path, required=True)
    parser.add_argument('--artifact-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('preserve existing evidence; choose a new output')
    texts, papers = {}, {}
    for key, meta in PAPERS.items():
        text_path, html_path = args.cache / f'{key}.txt', args.cache / f'{key}.html'
        text = norm(text_path.read_text(errors='ignore'))
        texts[key] = text
        papers[key] = dict(meta, abs_url=f"https://arxiv.org/abs/{meta['arxiv_id']}",
                           html_url=f"https://arxiv.org/html/{meta['arxiv_id']}{meta['version']}",
                           title_found_in_text=norm(meta['title']) in text,
                           title_found_ignoring_spaces=(re.sub(r'\s', '', meta['title']).lower()
                                                        in re.sub(r'\s', '', text).lower()),
                           html_sha256=sha256_file(html_path), html_bytes=html_path.stat().st_size,
                           text_sha256=sha256_file(text_path), text_chars=len(text),
                           cached_utc=dt.datetime.fromtimestamp(html_path.stat().st_mtime, dt.timezone.utc).isoformat())
    quotes = []
    for key, qid, quote in QUOTES:
        position = texts[key].find(norm(quote))
        quotes.append(dict(id=qid, paper=key, arxiv_id=PAPERS[key]['arxiv_id'], quote=quote,
                           found_verbatim=position >= 0, char_offset=position))
    # --- downloaded VERA artifact: data only, never imported or executed ---
    archive = zipfile.ZipFile(args.artifact_zip)
    names = archive.namelist()
    files = {}
    for path in sorted(p for p in args.artifact_dir.rglob('*') if p.is_file()):
        files[str(path.relative_to(args.artifact_dir))] = hashlib.sha256(path.read_bytes()).hexdigest()
    source_text = {rel: (args.artifact_dir / rel).read_text(errors='ignore')
                   for rel in files if rel.startswith('src/') and rel.endswith('.py')}
    risky = re.compile(r'import (socket|requests|urllib|http|subprocess|ftplib|smtplib|paramiko|ctypes)|from (urllib|http|subprocess|requests)|os\.system|eval\(|exec\(|__import__|pickle')
    conj = re.compile(r'all[-_ ]parent|threshold|quorum|conjunct|require_all|k-of-n|m-of-n', re.I)
    granularity = source_text.get('src/revocation/granularity.py', '')
    artifact = dict(
        paper_stated_url='https://anonymous.4open.science/r/ictai2026-agent-revocation-artifact-14BA/README.md',
        paper_stated_in='VERA arXiv:2608.30091v1, unnumbered Artifact Availability paragraph after Section XI (quote VERA-4)',
        archive_sha256=sha256_file(args.artifact_zip), archive_entries=len(names), file_count=len(files),
        file_sha256=files, executed=False,
        execution_status=('NOT EXECUTED. An attempt to run the downloaded artifact scripts/tests was denied by the '
                          'session permission classifier and was not retried or bypassed. Evidence below is static reading only.'),
        static_review=dict(
            source_files=sorted(source_text),
            risky_call_matches_in_src=sorted(f for f, t in source_text.items() if risky.search(t)),
            conjunctive_or_threshold_terms_in_src={f: sorted(set(m.group(0).lower() for m in conj.finditer(t)))
                                                   for f, t in source_text.items() if conj.search(t)},
            target_set_l2_defined='def target_set_l2' in granularity,
            target_set_l2_is_reachability_difference=('reachable_with - reachable_without' in granularity),
            handoff_recorded_as_candidate_edge=('Record a runtime caller-to-callee handoff as a candidate edge'
                                                in source_text.get('src/revocation/api.py', '')),
            e17_states_not_a_full_a2a_stack=('does not claim to implement the full A2A'
                                             in (args.artifact_dir / 'experiments/e17_a2a_protocol_demo/run.py').read_text(errors='ignore')
                                             .replace('\n', ' ').replace('A2A\nprotocol', 'A2A protocol')
                                             or 'It does not claim to implement the full A2A' in
                                             (args.artifact_dir / 'experiments/e17_a2a_protocol_demo/run.py').read_text(errors='ignore').replace('\n', ' '))))
    result = dict(classification='R3_PRIOR_ART_PROVENANCE', generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  papers=papers, quote_count=len(quotes), quotes_found=sum(q['found_verbatim'] for q in quotes),
                  quotes=quotes, vera_artifact=artifact,
                  note='Paper texts are cached locally (not committed). Hashes identify the exact HTML versions read.')
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'papers': len(papers), 'titles_found': sum(p['title_found_in_text'] for p in papers.values()),
                      'titles_found_ignoring_spaces': sum(p['title_found_ignoring_spaces'] for p in papers.values()),
                      'quotes': len(quotes), 'quotes_found': result['quotes_found'],
                      'artifact_files': len(files), 'artifact_executed': False}))
    return 0 if result['quotes_found'] == len(quotes) else 1


if __name__ == '__main__':
    sys.exit(main())
