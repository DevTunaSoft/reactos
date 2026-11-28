#!/usr/bin/env python3
"""Original ProjectOS V7 record builder: local verified state -> sanitized repo JSONL.

Writes only under docs/projectos/research/ in the authorized research worktree.
No credentials, local absolute paths, raw patch bodies or third-party code.
"""
import json
import os
import shutil
import sys
from datetime import datetime, timezone

REPO = os.environ.get("PROJECTOS_V7_REPO", ".")
BASE = os.environ.get("PROJECTOS_V7_STATE",
                      os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state"))
DEST = os.path.join(REPO, "docs", "projectos", "research")
J = lambda x: json.dumps(x, sort_keys=True)


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(name):
    return [json.loads(l) for l in open(os.path.join(BASE, name), encoding="utf-8") if l.strip()]


def write_lines(name, rows):
    p = os.path.join(DEST, name)
    with open(p, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(J(r) + "\n")
    print(name, len(rows), os.path.getsize(p), "bytes")


def main():
    os.makedirs(DEST, exist_ok=True)
    now = utc()

    forks = load("fork_network_enriched.jsonl")
    compact_forks = [{
        "id": r["id"], "full_name": r["full_name"],
        "parent_verified": r.get("parent_verified"),
        "lineage_status": r.get("lineage_status"),
        "archived": r.get("archived"), "pushed_at": r.get("pushed_at"),
        "default_branch": r.get("default_branch"),
        "url": r.get("source_url"), "method": "REST fork-list + GraphQL parent lookup",
        "retrieved": "2026-11-27T05:40:23Z",
    } for r in forks]
    write_lines("FORK_NETWORK_V7.jsonl", compact_forks)

    cands = load("candidates_validated.jsonl")
    compact_cands = [{
        "id": r["id"], "name": r["repository"], "current_full_name": r.get("current_full_name"),
        "live_status": r.get("live_status"), "parent": r.get("parent"),
        "in_verified_fork_network": r["repository"] in {x["full_name"] for x in forks},
        "verification": r.get("verification"), "retrieved": r.get("retrieved"),
    } for r in cands]
    write_lines("CANDIDATE_VALIDATION_V7.jsonl", compact_cands)

    rev = load("revalidation.jsonl")
    write_lines("REVALIDATION_V7.jsonl", rev)
    pe = load("patch_equivalence.jsonl")
    write_lines("PATCH_EQUIVALENCE_V7.jsonl", pe)

    # Canonical findings: exact source, observed fact, classification, decision.
    findings = [
        {
            "id": "FV7-001", "retrieved": "2026-11-27T05:27:02Z",
            "source_ids": ["S-V7-01", "S-V7-02"],
            "url": "https://github.com/DevTunaSoft/reactos/blob/research/v7-wave1/docs/projectos/research/FORK_NETWORK_V7.jsonl",
            "sha": "3e6033a613fbf7c5bd58aaeaa05af42514af59d5",
            "claimed": "Prior record enumerated 999 name-search candidates and 294 branch entries.",
            "observed": "Authenticated paginated fork list returned 2426 unique repository IDs; GraphQL verified parent=reactos/reactos for 2336; 90 lineage-unresolved; 12 archived; 0 disabled.",
            "upstream_status": "N/A (inventory)", "subsystem": "coverage", "issue_ids": [],
            "confidence": "high", "prerequisites": ["GitHub read credentials"], "risk": "none",
            "hypothesis": "Prior name search under-counted the true fork network and conflated name matches with lineage.",
            "verification_plan": "Re-run GET /repos/reactos/reactos/forks with --paginate; compare stable IDs and parent IDs.",
            "evidence_class": "direct_api_observation", "reviewer": "pending_independent",
            "decision": "Accept as coverage correction; retain prior record unchanged.",
        },
        {
            "id": "FV7-002", "retrieved": "2026-11-27T05:40:23Z",
            "source_ids": ["S-V7-03"],
            "url": "https://github.com/DevTunaSoft/reactos/blob/research/v7-wave1/docs/projectos/research/CANDIDATE_VALIDATION_V7.jsonl",
            "sha": "3e6033a613fbf7c5bd58aaeaa05af42514af59d5",
            "claimed": "999 candidate IDs from repository name search, parent unverified.",
            "observed": "999/999 still public; 0 renamed; 910/999 IDs present in verified fork network; 89 outside it. No unavailable/private candidates observed by name lookup or ID fallback.",
            "upstream_status": "N/A (validation)", "subsystem": "coverage", "issue_ids": [],
            "confidence": "high", "prerequisites": [], "risk": "none",
            "hypothesis": "Name-search candidates are not equivalent to fork-network membership.",
            "verification_plan": "Cross-check candidate numeric IDs against FORK_NETWORK_V7.jsonl IDs.",
            "evidence_class": "direct_api_observation", "reviewer": "pending_independent",
            "decision": "Append correction to prior inventory; do not describe the 999 as forks.",
        },
        {
            "id": "FV7-003", "retrieved": "2026-11-27T05:43:00Z",
            "source_ids": ["S-V7-04", "S-V7-05"],
            "url": "https://github.com/reactos/reactos/pull/1965",
            "sha": "77e2dc42a0c3a58747d0b86cf612a78f21e77162",
            "claimed": "F-02 FreeLoader Btrfs unaligned-read change treated as potential improvement.",
            "observed": "git patch-id --stable of fork commit f79381e5 and upstream PR #1965 merge commit 77e2dc42 are identical (ecb96617); PR merged 2019-10-30.",
            "upstream_status": "ALREADY_FIXED", "subsystem": "storage/boot", "issue_ids": [],
            "confidence": "high", "prerequisites": [], "risk": "none",
            "hypothesis": "The fork change is a byte-equivalent upstream contribution.",
            "verification_plan": "Recompute patch-id from both immutable .patch URLs; confirm merge state.",
            "evidence_class": "patch_identity", "reviewer": "pending_independent",
            "decision": "Remove F-02 from engineering candidate queue; preserve as historical evidence.",
        },
        {
            "id": "FV7-004", "retrieved": "2026-11-27T05:43:00Z",
            "source_ids": ["S-V7-06", "S-V7-07"],
            "url": "https://github.com/reactos/reactos/pull/1070",
            "sha": "3ba51dc21894bd5c2d1574af1db5094ab4e3d6ae",
            "claimed": "F-07 MiCheckForUserStackOverflow variable spelling commit.",
            "observed": "patch-id a1c40064 identical to upstream PR #1070 merge; merged 2018-12-12. Prior round already deprioritized it.",
            "upstream_status": "ALREADY_FIXED", "subsystem": "memory", "issue_ids": [],
            "confidence": "high", "prerequisites": [], "risk": "none",
            "hypothesis": "Branch name was a false positive.",
            "verification_plan": "Recompute patch-id from immutable URLs.",
            "evidence_class": "patch_identity", "reviewer": "pending_independent",
            "decision": "Confirm prior deprioritization.",
        },
        {
            "id": "FV7-005", "retrieved": "2026-11-27T05:43:00Z",
            "source_ids": ["S-V7-08", "S-V7-09"],
            "url": "https://github.com/reactos/reactos/pull/1959",
            "sha": "90ac794bf284f4c2b78b532dc02fcf9275783209",
            "claimed": "F-03 branch handles Btrfs sparse extents; tip is style-only.",
            "observed": "Tip patch-id d9e871bd and functional parent aad76695 patch-id 688b412e both differ from upstream PR #1959 merge patch-id 4a99100f (merged 2019-10-08). Behavioural equivalence not established.",
            "upstream_status": "EQUIVALENCE_UNKNOWN", "subsystem": "storage/boot", "issue_ids": [],
            "confidence": "medium", "prerequisites": ["behavioral comparison on sparse extent images"],
            "risk": "data integrity if misclassified",
            "hypothesis": "Two independently developed sparse-extent implementations may share behavior without shared expression.",
            "verification_plan": "Compare behavior on synthetic sparse Btrfs images; do not import code.",
            "evidence_class": "patch_nonidentity", "reviewer": "pending_independent",
            "decision": "Keep as NEEDS_SEMANTIC_COMPARISON; not engineering-ready.",
        },
        {
            "id": "FV7-006", "retrieved": "2026-11-27T05:30:00Z",
            "source_ids": ["S-V7-10", "S-V7-11", "S-V7-12"],
            "url": "https://github.com/reactos/reactos/pull/9646",
            "sha": "065abb35f5e8",
            "claimed": "F-05/F-06 2017 GSoC xHCI work treated as still relevant; CORE-13344 Open.",
            "observed": "PR #9646 merged 2026-11-06 importing USB3 drivers incl. usbxhci; PR #9623 merged 2026-10-09 building new USB3 architecture. PRs #1823 and #1694 (older imports) closed unmerged. JIRA CORE-13344 remains Open, updated 2026-11-06.",
            "upstream_status": "PARTIALLY_SUPERSEDED", "subsystem": "usb/pnp", "issue_ids": ["CORE-13344"],
            "confidence": "high", "prerequisites": ["verify actual controller behavior"], "risk": "medium",
            "hypothesis": "Historical GSoC code is primarily regression/design evidence, not a current patch source.",
            "verification_plan": "Compare current drivers/usb/usbxhci behavior to issue acceptance criteria; no tests run.",
            "evidence_class": "upstream_status_change", "reviewer": "pending_independent",
            "decision": "Reprioritize F-05/F-06 as historical archaeology; do not resurrect.",
        },
        {
            "id": "FV7-007", "retrieved": "2026-11-27T05:30:00Z",
            "source_ids": ["S-V7-13", "S-V7-14", "S-V7-15"],
            "url": "https://github.com/reactos/reactos/pull/8713",
            "sha": "3e6033a613fbf7c5bd58aaeaa05af42514af59d5",
            "claimed": "F-04 TheNNX WoW64 work linked to CORE-17655.",
            "observed": "PR #8713 (kernel WoW64 prep) merged 2026-08-06; PR #9766 (kbd.h WoW64 prep) merged 2026-11-07. At pinned baseline the tree contains sdk/lib/rtl/wow64.c and a ntdll winetest, but no wow64 implementation subtree. JIRA CORE-17655 is Reopened, updated 2026-10-01.",
            "upstream_status": "PREREQUISITES_LANDED", "subsystem": "wow64/loader", "issue_ids": ["CORE-17655"],
            "confidence": "high", "prerequisites": ["ABI probe design", "exact branch diff review"], "risk": "high",
            "hypothesis": "Some prerequisites that were absent for older WoW64 patches now exist, changing feasibility.",
            "verification_plan": "Review TheNNX five commits against current upstream file set and ABI contracts; no tests run.",
            "evidence_class": "upstream_status_change", "reviewer": "pending_independent",
            "decision": "Revalidate F-04 branch against current baseline before ranking.",
        },
        {
            "id": "FV7-008", "retrieved": "2026-11-27T05:30:00Z",
            "source_ids": ["S-V7-16", "S-V7-17"],
            "url": "https://github.com/reactos/reactos/pull/9795",
            "sha": "8b55d712a75d2da462a96adff4f6684c0b43e2d6",
            "claimed": "F-08 ARM64 debug services work linked to CORE-18200.",
            "observed": "Cited CI commit 8b55d71 dates 2022-05-25 and built only some applications. PRs #9795, #9781, #9780, #9762, #9772, #9771, #9765 are merged/closed with 2026 dates; CORE-18200 remains Open (updated 2025-07-04).",
            "upstream_status": "ACTIVE_UPSTREAM_WORK", "subsystem": "arm64", "issue_ids": ["CORE-18200"],
            "confidence": "medium", "prerequisites": ["ARM64 unwind contract verification"], "risk": "high",
            "hypothesis": "ARM64 candidate overlap must be rechecked against much newer upstream work.",
            "verification_plan": "Enumerate merged ARM64 commits since 2026-08 and compare file/symbol sets.",
            "evidence_class": "upstream_status_change", "reviewer": "pending_independent",
            "decision": "Do not rank F-08 until overlap check is complete; tests NOT RUN.",
        },
        {
            "id": "FV7-009", "retrieved": "2026-11-27T05:45:00Z",
            "source_ids": ["S-V7-18", "S-V7-19"],
            "url": "https://github.com/reactos/reactos/pull/9510",
            "sha": "3e6033a613fbf7c5bd58aaeaa05af42514af59d5",
            "claimed": "Closed-unmerged PR #9510 proposed bounds/validity checks in FreeLoader FAT and NTFS drivers, including bounded FatCountClustersInChain, nonzero power-of-two BytesPerSector, LFN sequence bounds and short-read detection.",
            "observed": "At pinned baseline boot/freeldr/freeldr/lib/fs/fat.c lines 1108-1133 FatCountClustersInChain loops until an end-of-chain marker with no cluster-count bound; line 320/335 assign BytesPerSector directly from boot sector. PR #9510 is closed unmerged (2026-09-09), no maintainer comment returned by REST. JIRA text search for 'cluster chain' returned 6 issues, none about FreeLoader boot hang.",
            "upstream_status": "OPEN_LEAD", "subsystem": "storage/boot", "issue_ids": [],
            "confidence": "medium", "prerequisites": ["independent review", "crafted FAT image", "disposable VM if test authorization exists"],
            "risk": "high (boot-time memory corruption on malformed image)",
            "hypothesis": "A cyclic or invalid FAT cluster chain can cause unbounded traversal/short reads during boot; an independent bounded implementation may be warranted.",
            "verification_plan": "Design synthetic FAT12/16/32 images with cyclic chain and invalid BytesPerSector; run only in approved disposable environment; record NOT RUN until executed.",
            "evidence_class": "source_plus_closed_upstream_pr", "reviewer": "pending_independent",
            "decision": "STRONG_CANDIDATE for engineering packet; research only, no code change, provenance route A requires per-file review.",
        },
    ]
    write_lines("FINDINGS_V7.jsonl", findings)

    issues = [
        {"issue_id": "CORE-17655", "url": "https://jira.reactos.org/browse/CORE-17655",
         "severity": "high", "impact": "32-bit installers unavailable on x64", "baseline_sha": "3e6033a6",
         "status": "Reopened", "updated": "2026-10-01T13:59:50.000+0000",
         "reproducer": "VirtualBox Guest Additions 6.1.18 32-bit installer on x64 build 0.4.15-dev-2738",
         "suspected_root_cause": "No WoW64 subsystem; prerequisites only recently merged",
         "alternatives": ["installer misdetection", "missing loader thunks"],
         "matching_findings": ["FV7-007"], "equivalence_status": "PREREQUISITES_LANDED",
         "dependency_chain": ["PR #8713 merged", "PR #9766 merged"],
         "proposed_minimal_intervention": "First produce ABI/behavior specification and candidate packet; no implementation",
         "acceptance": "32-bit installer completes on x64", "regression": "native x64 apps unaffected",
         "provenance": "research-only; route A candidate pending review", "confidence": "medium",
         "missing_evidence": ["current branch diff review", "runtime reproduction NOT RUN"]},
        {"issue_id": "CORE-13344", "url": "https://jira.reactos.org/browse/CORE-13344",
         "severity": "high", "impact": "USB3 ports unusable", "baseline_sha": "3e6033a6",
         "status": "Open", "updated": "2026-11-06T07:08:33.000+0000",
         "reproducer": "USB device attached to xHCI controller",
         "suspected_root_cause": "historical absence of xHCI driver; modern stack imported 2026-11",
         "alternatives": ["setup INF not installing stack", "controller-specific regressions"],
         "matching_findings": ["FV7-006"], "equivalence_status": "PARTIALLY_SUPERSEDED",
         "dependency_chain": ["PR #9623 merged", "PR #9646 merged", "PR #9865 open"],
         "proposed_minimal_intervention": "Verify current stack against acceptance criteria before any change",
         "acceptance": "USB3 storage/input works", "regression": "USB2 stack unaffected",
         "provenance": "historical GSoC work GPLv2+ headers observed; no import", "confidence": "high",
         "missing_evidence": ["runtime reproduction NOT RUN"]},
        {"issue_id": "CORE-18200", "url": "https://jira.reactos.org/browse/CORE-18200",
         "severity": "high", "impact": "ARM64 port incomplete", "baseline_sha": "3e6033a6",
         "status": "Open", "updated": "2025-07-04T22:44:02.000+0000",
         "reproducer": "umbrella tracking issue, no single reproducer",
         "suspected_root_cause": "multiple missing subsystems",
         "alternatives": ["toolchain gaps", "unwind ABI gaps"],
         "matching_findings": ["FV7-008"], "equivalence_status": "ACTIVE_UPSTREAM_WORK",
         "dependency_chain": ["PR #9795 etc. merged"],
         "proposed_minimal_intervention": "Build symbol/file overlap matrix before ranking branches",
         "acceptance": "native/emulated ARM64 exception unwind works", "regression": "other architectures unaffected",
         "provenance": "research only", "confidence": "medium",
         "missing_evidence": ["ARM64 runtime tests NOT RUN"]},
        {"issue_id": "NO_CANONICAL_ISSUE-FAT-BOOT-001",
         "url": "https://github.com/reactos/reactos/pull/9510",
         "severity": "high", "impact": "potential boot hang or buffer overrun on malformed FAT image",
         "baseline_sha": "3e6033a6", "status": "LEAD", "updated": "2026-09-09T12:15:31Z",
         "reproducer": "synthetic malformed FAT image (designed, NOT RUN)",
         "suspected_root_cause": "unbounded FatCountClustersInChain and missing on-disk field validation",
         "alternatives": ["malformed image outside supported set", "other boot path"],
         "matching_findings": ["FV7-009"], "equivalence_status": "NO_UPSTREAM_EQUIVALENT_FOUND",
         "dependency_chain": [],
         "proposed_minimal_intervention": "independently specified bounded traversal + validation; no code in this mandate",
         "acceptance": "malformed image rejected with error, no hang/overrun", "regression": "valid FAT12/16/32 boots unchanged",
         "provenance": "upstream PR closed unmerged; route A/B undecided, quarantine until reviewed",
         "confidence": "medium",
         "missing_evidence": ["JIRA text search returned 6 unrelated issues", "test NOT RUN", "independent review pending"]},
    ]
    write_lines("ISSUE_CORRELATION_V7.jsonl", issues)

    sources = [
        {"id": "S-V7-01", "url": "https://github.com/reactos/reactos/forks?sort=oldest", "revision": "retrieved 2026-11-27T05:20Z", "method": "gh api --paginate REST", "classification": "approved_public", "license": "per-repository, not inherited", "notes": "link-following via gh --paginate"},
        {"id": "S-V7-02", "url": "https://docs.github.com/en/graphql", "revision": "retrieved 2026-11-27T05:40Z", "method": "gh api graphql batches of 100", "classification": "approved_public", "license": "N/A", "notes": "parent database IDs verified for 2336 forks"},
        {"id": "S-V7-03", "url": "https://github.com/DevTunaSoft/reactos/blob/research/fork-archaeology-2026-11-26/docs/projectos/research/FORK_SEARCH_CANDIDATES_2026-11-26.jsonl", "revision": "5c02f5c5", "method": "raw retrieval", "classification": "inherited_research_record", "license": "project research", "notes": "999 candidate IDs"},
        {"id": "S-V7-04", "url": "https://github.com/maharmstone/reactos/commit/f79381e5fa59dada4375ac605c2afa439c7bab7d", "revision": "f79381e5", "method": "commit .patch", "classification": "licensed_foss_candidate", "license": "per-file review pending", "notes": "F-02"},
        {"id": "S-V7-05", "url": "https://github.com/reactos/reactos/pull/1965", "revision": "77e2dc42", "method": "REST PR + commit .patch", "classification": "approved_upstream", "license": "ReactOS upstream", "notes": "merged 2019-10-30"},
        {"id": "S-V7-06", "url": "https://github.com/andrew-boyarshin/reactos/commit/a54b334625a43fd56ab889369aa28e2382d9cbc1", "revision": "a54b3346", "method": "commit .patch", "classification": "licensed_foss_candidate", "license": "per-file review pending", "notes": "F-07"},
        {"id": "S-V7-07", "url": "https://github.com/reactos/reactos/pull/1070", "revision": "3ba51dc2", "method": "REST PR + commit .patch", "classification": "approved_upstream", "license": "ReactOS upstream", "notes": "merged 2018-12-12"},
        {"id": "S-V7-08", "url": "https://github.com/maharmstone/reactos/commit/98880e55aa6bf4ca24dfa8313783b38d92a94adf", "revision": "98880e55", "method": "commit .patch", "classification": "licensed_foss_candidate", "license": "per-file review pending", "notes": "F-03 tip, style-only"},
        {"id": "S-V7-09", "url": "https://github.com/reactos/reactos/pull/1959", "revision": "90ac794b", "method": "REST PR + commit .patch", "classification": "approved_upstream", "license": "ReactOS upstream", "notes": "merged 2019-10-08"},
        {"id": "S-V7-10", "url": "https://jira.reactos.org/browse/CORE-13344", "revision": "updated 2026-11-06", "method": "JIRA REST", "classification": "approved_public", "license": "N/A", "notes": "issue text untrusted"},
        {"id": "S-V7-11", "url": "https://github.com/reactos/reactos/pull/9646", "revision": "065abb35", "method": "REST PR + commit list", "classification": "approved_upstream", "license": "ReactOS upstream", "notes": "merged 2026-11-06"},
        {"id": "S-V7-12", "url": "https://github.com/reactos/reactos/pull/1823", "revision": "closed unmerged", "method": "REST PR", "classification": "failure_archaeology", "license": "N/A", "notes": "historical xHCI import"},
        {"id": "S-V7-13", "url": "https://jira.reactos.org/browse/CORE-17655", "revision": "updated 2026-10-01", "method": "JIRA REST", "classification": "approved_public", "license": "N/A", "notes": "issue text untrusted"},
        {"id": "S-V7-14", "url": "https://github.com/reactos/reactos/pull/8713", "revision": "merged 2026-08-06", "method": "REST PR", "classification": "approved_upstream", "license": "ReactOS upstream", "notes": "WoW64 kernel prep"},
        {"id": "S-V7-15", "url": "https://github.com/reactos/reactos/pull/9766", "revision": "merged 2026-11-07", "method": "REST PR", "classification": "approved_upstream", "license": "ReactOS upstream", "notes": "kbd.h WoW64 prep"},
        {"id": "S-V7-16", "url": "https://jira.reactos.org/browse/CORE-18200", "revision": "updated 2025-07-04", "method": "JIRA REST", "classification": "approved_public", "license": "N/A", "notes": "umbrella issue"},
        {"id": "S-V7-17", "url": "https://github.com/reactos/reactos/commit/8b55d712a75d2da462a96adff4f6684c0b43e2d6", "revision": "8b55d71", "method": "REST commit", "classification": "approved_upstream", "license": "ReactOS upstream", "notes": "2022 CI builder, apps only"},
        {"id": "S-V7-18", "url": "https://github.com/reactos/reactos/pull/9510", "revision": "56b5899d", "method": "REST PR + comments", "classification": "failure_archaeology", "license": "unadopted upstream proposal", "notes": "closed unmerged, no comments returned"},
        {"id": "S-V7-19", "url": "https://github.com/reactos/reactos/blob/3e6033a613fbf7c5bd58aaeaa05af42514af59d5/boot/freeldr/freeldr/lib/fs/fat.c", "revision": "3e6033a6", "method": "raw source read", "classification": "approved_upstream_source", "license": "ReactOS GPLv2+ (per-file review pending)", "notes": "lines 320/335/1108-1133"},
    ]
    write_lines("SOURCE_REGISTER_V7.jsonl", sources)

    failures = [
        {"id": "FA-V7-001", "objective": "Validate on-disk FreeLoader FAT/NTFS data before use",
         "revision": "PR head 56b5899d", "environment": "upstream PR CI",
         "approach": "bounds and validity checks in fat.c/ntfs.c",
         "observed": "closed unmerged 2026-09-09; no maintainer comment via REST; current baseline still has unbounded FatCountClustersInChain",
         "reproduction": "not reproduced", "first_last_affected": "unknown",
         "likely_cause": "review/acceptance unknown - motive not inferred",
         "competing_hypotheses": ["fix unnecessary", "superseded elsewhere", "insufficient evidence"],
         "missing_prerequisite": "unknown", "later_changes": "none found for this function",
         "safe_next_step": "independent behavioral test design; no code import",
         "links": ["https://github.com/reactos/reactos/pull/9510", "FV7-009"]},
        {"id": "FA-V7-002", "objective": "Import 2017 GSoC xHCI driver",
         "revision": "PRs #1694/#1823", "environment": "upstream 2019-2020",
         "approach": "import Lesan/GSoC driver",
         "observed": "both closed unmerged; modern USB3 stack imported via merged PRs #9623/#9646 in 2026",
         "reproduction": "historical compile failures reported upstream", "first_last_affected": "2017-2020",
         "likely_cause": "architecture superseded", "competing_hypotheses": ["historical toolchain mismatch"],
         "missing_prerequisite": "modern UCX/USB hub architecture", "later_changes": ["PR #9623", "PR #9646"],
         "safe_next_step": "treat as design/regression source only",
         "links": ["https://github.com/reactos/reactos/pull/1823", "FV7-006"]},
    ]
    write_lines("FAILURE_MODE_INDEX_V7.jsonl", failures)

    # Sanitized queue snapshot: no lease owner identities beyond generic worker IDs.
    qsrc = os.path.join(BASE, "queue_state.json")
    rows = []
    if os.path.exists(qsrc):
        st = json.load(open(qsrc, encoding="utf-8"))
        for tid, t in sorted(st["tasks"].items()):
            rows.append({k: t.get(k) for k in ("id", "title", "lane", "priority", "status",
                                               "attempts", "next_action", "evidence", "blocker")})
    write_lines("QUEUE_SNAPSHOT_V7.jsonl", rows)

    # Sanitized tool copies (no credentials, no absolute personal paths in code).
    tdir = os.path.join(DEST, "tools")
    os.makedirs(tdir, exist_ok=True)
    for name in ("supervisor.py", "collect_network.py", "revalidate_findings.py", "build_records.py"):
        src = os.path.join(os.path.dirname(BASE), "tools", name)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(tdir, name))
            print("tool copied:", name)
    print("done", now)


if __name__ == "__main__":
    sys.exit(main())
