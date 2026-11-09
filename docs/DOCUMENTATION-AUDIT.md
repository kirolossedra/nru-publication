# Documentation audit

**Audit date:** 2026-11-09  
**Scope:** Root README, governance, architecture/methodology, Missions 1/2/2.5, decision records, and template in the original Mission 2.5 audit; Mission 3 verification is appended chronologically below.

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

## Mission 3 experiment and documentation audit (2026-11-09)

### Evidence and implementation checks

- Reviewed `scripts/run_mission3.py`, `scripts/analyze_mission3.py`, the Mission 3 source diff, fixed pilot JSON, all run configs, validation sidecars, and generated metric tables.
- Incremental build completion is recorded in `logs/build-mission3-traffic-stop.log`. The optional `trafficStopTime` defaults to the existing simulation stop; an execution with default timing matched the saved Mission 1 SQLite E2E throughput, byte counts, mean delay, and jitter. No PHY/MAC protocol logic was changed.
- The analyzer discovered 39 unique run directories: 35 completed and 4 failed. All 24 primary revised mixed/reference executions completed. The four failures are indexed in [`failed-runs.csv`](../results/mission3/analysis/failed-runs.csv), with configs and full logs retained locally.
- The 18 common-horizon mixed pilot runs and 6 single-technology references contain 49,838 TX rows and 49,838 unique RX rows. Their sidecars report zero duplicates, unmatched receptions, and packets not received by stop. The validator checks TX-key uniqueness, timestamps/status, sidecar totals, and expected SQLite table names.
- Seed/configuration claims were checked against `configs/mission3-pilot.json` and per-run `run-config.json`; numerical claims and plotted inputs were checked against `condition-summary.csv` and `seed-run-metrics.csv`. Application payload throughput is derived from packet counts and 1000-byte packet size; FlowMonitor IP throughput is reported separately. Occupancy uses the example's existing SQLite statistic.
- Both Python scripts passed syntax compilation. The analyzer generated the metric tables and five figures; figures were visually inspected. Matplotlib gave a nonfatal optional Axes3D import warning; required 2D plots completed.
- The mission report labels P99.9 exploratory, distinguishes across-run Student-t intervals from packet quantiles, notes the identical 12 Mbps NR seed means as an unresolved observation, and avoids claims of congestion, saturation, causality, novelty, or real-world validation.
- After all experiments, `df -h .` showed 17 GiB available; `du -sh source/ns-3-dev` reported 3.2 GiB and all `results/mission3` artifacts 9.7 MiB. The host remains above the 10 GiB free-space requirement.

### Documentation and reproducibility checks

- Root README, mission index, Mission 3 report, experimental methodology, and D-006 were updated. The report includes the fixed parameter table and links the existing topology and experiment-workflow diagrams.
- Reproduction commands use the existing compiled binary, exact rates, seeds, and timing. The runner refuses to overwrite existing run folders. Each local execution has its own config, log, packet CSV/sidecar, and SQLite database.
- Raw per-run folders are gitignored; aggregate/seed/failure CSVs and five PNGs are available as compact outputs. No upstream simulator source or compiled artifact is intended for publication.
- Earlier Mission 2.5 text stating Mission 3 had not started is historical and superseded by this addendum and the completed Mission 3 report.

### Claims not independently established

- No Mermaid renderer was used; diagram fences and syntax were reviewed manually. Figures were visually inspected, but no independent plotting test framework exists.
- The simulator cannot identify why a packet absent at stop is missing; primary runs observed none. Existing outputs do not attribute delay to LBT defer/backoff, retransmissions, or PHY/MAC drops. No such causal claim is made.
- The 4.9 s horizon avoids the observed longer-run assertion but does not establish scheduler correctness or steady-state operation. The identical NR high-load means have an unknown explanation. 12 Mbps did not establish saturation.
- The 10,000-sample P99.9 threshold leaves only about 16 observations in the top 0.1%; P99.9 is an exploratory empirical value, not a conclusive tail estimate.

### Publication audit (pre-commit; 2026-11-09)

- `gh auth status` confirmed active authenticated account `kirolossedra`; `git fetch origin main` succeeded. Local `main` and `origin/main` both pointed at Mission 1/2/2.5 commit `08a1586ca0cb4f45b136afe7299fb7374d26932d`, so the Mission 3 commit can be a normal fast-forward.
- Exactly 21 intended files were staged: `.gitignore`, README, Mission 3 config/report/decision, mission index, methodology, audit, incremental source patch, build log, runner/analyzer, three aggregate CSVs, and five figures. Total staged content was about 632 KB; the largest file was `mixed-vs-single-technology.png` at 147,269 bytes.
- Staged-path audit found no `source/`, build tree, object/library/executable path, or other simulator third-party source. All raw Mission 3 run directories are excluded by `.gitignore`; a representative packet CSV and SQLite path were confirmed ignored. Only compact validated aggregate outputs are staged.
- A pattern scan of staged text found no GitHub token, AWS access-key, or private-key marker. This scan is limited to those patterns and is not proof that no possible secret exists.
- Relative Markdown link check found 0 broken paths across 26 Markdown files. Seven Mermaid fences are present (the five required project diagrams plus Mission 3's topology/workflow diagrams); syntax was inspected manually, not renderer-validated.
- `git diff --check` passed. Repository URL: `https://github.com/kirolossedra/nru-publication`.
- The Mission 3 patch was reconstructed as an incremental diff from the exact pinned NR-U commit plus the Mission 2 latency patch; `git apply --unidiff-zero --check` and application in a temporary reconstruction confirmed it yields the installed Mission 3 source exactly. Its zero-context form is deliberate and the required apply option is documented in the Mission 3 report.

Commit SHA, push confirmation, remote tree verification, and final worktree status are appended after publication.
