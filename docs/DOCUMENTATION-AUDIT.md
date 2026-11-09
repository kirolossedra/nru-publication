# Documentation audit

**Audit date:** 2026-11-09  
**Scope:** Root README, governance, architecture/methodology, Missions 1/2/2.5, decision records, and template. This is a documentation/evidence audit only; no new simulation or simulator rebuild was run.

## Checks performed

- Walked Markdown files and resolved local relative link destinations. The initial audit found two links targeting this not-yet-created audit file itself; this file now exists. Re-run the command below after later documentation changes.
- Counted five Mermaid blocks: research architecture, network topology, packet-flow sequence, research workflow, and mission lifecycle. All use fenced `mermaid` code blocks and standard flowchart/sequence constructs. No Mermaid renderer is installed/used here, so visual rendering was not independently checked.
- Compared stack revisions with `manifests/commits.txt` and source repository `git rev-parse HEAD` values during the mission work.
- Checked baseline packet counts in `results/per-packet-latency.csv.validation.txt`; checked NR/Wi-Fi counts and calculated values against `results/latency-analysis/latency-summary.csv`.
- Checked Mission 1 values against the preserved `results/baseline.db` SQLite schema and rows. The prior Mission 1 vs instrumented E2E equality check is described in the Mission 2 report; the run's instrumented database is generated under `source/ns-3-dev/`.
- Verified successful build/run status from `logs/build-resume-1.log`, `logs/build-latency-instrumentation.log`, `logs/baseline.log`, and `logs/baseline-instrumented.log`.
- Confirmed mission index and root README link to the primary documentation and that root `AGENTS.md` specifies the future documentation completion gate.

## Recheck local Markdown links

Run from project root:

```sh
python3 - <<'PY'
from pathlib import Path
import re
missing=[]
for md in Path('.').rglob('*.md'):
    if 'source' in md.parts or 'build' in md.parts or '.git' in md.parts:
        continue
    for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', md.read_text()):
        target=target.split('#',1)[0].strip()
        if target and '://' not in target and not target.startswith('mailto:'):
            if not (md.parent/target).resolve().exists():
                missing.append((md,target))
for md,target in missing: print(f'{md} -> {target}')
print(f'broken relative links: {len(missing)}')
PY
```

This checks link destinations but not Markdown anchor names or external URL availability.

## Numerics verified

- Mission 2 validation sidecar: 124 TX records, 124 unique receives, 0 not received by stop, 0 duplicates, 0 unmatched.
- Analysis CSV: NR 62/62, mean 3377.6470645161285 µs; Wi-Fi 62/62, mean 172.79108064516126 µs. Mission reports round these to 3377.6 and 172.8 µs.
- Mission 1 baseline SQLite has NR/Wi-Fi E2E rows with 63,736 TX/RX bytes each, 0.509888 Mbps each, mean delays 3377 and 172 µs, mean jitter 64 and 84 µs, occupancy 0.047141843 and 0.014472. The summary rounds values; raw DB is authoritative.
- Exact commits are in `manifests/commits.txt`.

## Claims not independently verified / limitations

- The installed example source identifies 802.11ax and LBT manager types, and the baseline executes those settings. This audit does not validate standards conformance or real-world behavior.
- Cat 2/Cat 3, scenario 1, other rate modes, and alternative access managers are source-supported options but were not executed in the saved baseline.
- The build host's full package inventory and exact compiler version were not saved in the original installation manifest; only OS, CMake, Python, Git, successful build, and configure summary are documented. Do not claim exact dependency versions beyond these records.
- Mission 2 analyzer dependency versions (NumPy/Matplotlib) were not frozen in a lock/requirements file. The modules were available and plots generated; version-pinned reproduction is outstanding.
- Mission 2's first unsuccessful flow-matching run was overwritten at the same log path by the successful retry. Its unmatched counts were observed during the debugging turn but no separate failed-run artifact remains. This is disclosed in the Mission 2 report and is a process gap to avoid going forward.
- Duplicate handling branch is implemented and source-reviewed, but no duplicate was observed in baseline; actual duplicate-path execution remains unverified. Similarly, baseline had no nonreceipts, so loss-path behavior was source-reviewed, not exercised by a lossy run.
- Mermaid blocks were checked for placement and recognizable syntax, not rendered by a Mermaid parser.
- No external link status check was performed; official source URLs are recorded in Mission 1 docs.

## Outcome

The documentation index and governance are in place; the checked paths, numerical claims, source references, and saved logs support the completion claims for Missions 1 and 2. The unverified details above remain explicit and must not be promoted to verified facts without additional evidence. Mission 3 has not started.
- The Mission 2 example initially failed to compile because `Ipv4Address::ToString()` is unavailable in ns-3.35; implementation switched to `Ipv4Address::Print`. The failed build log was overwritten by the successful retry at the same path. Mission 2 report now records the root cause and evidence gap; no protocol logic changed.
- The Mission 2 instrumented SQLite database and Mission 1/2 comparison output are now preserved as `results/mission2-instrumented.db` and `results/mission2-sqlite-comparison.txt`; the recorded E2E query diff is empty.
- Final local-link scan: 0 broken relative file links across 24 project Markdown files. Five Mermaid blocks were found in the required locations. Mermaid was not rendered by a parser.

## GitHub publication preparation (2026-11-09)

- Verified `gh auth status` for the active `kirolossedra` account; repository `kirolossedra/nru-publication` is public and defaults to `main`.
- Inspected a temporary clone. Remote `main` contained one initial commit (`041cd2a`) with a one-line README. The existing project directory had no Git metadata. Local Git was initialized in place and based on `origin/main` with a mixed reset that left the existing working files intact; the original remote commit remains in history.
- Added `.gitignore` rules for the entire `source/` tree, build products, caches, temporary artifacts, credentials, and large generated data. Explicit small validated SQLite/CSV exceptions remain stageable.
- Staged only root project policy, docs, config, logs, manifests, patches, scripts, template, small SQLite/CSV outputs, and PNG figures. No `source/` path was staged. The largest intended file is the 103,909-byte build log.
- Scanned staged text for common GitHub/AWS credential forms/private-key markers; none were found. This is a pattern scan, not proof that no secret of any form exists.
- Both source patches passed `git apply --check` against files extracted from the exact pinned ns-3 and NR-U commits. `scripts/install-environment.sh` passed `bash -n` and refuses to reuse an existing `source/` directory.
- Publication commit and push details are provided in the completion report; no force push or branch change is authorized or used.
