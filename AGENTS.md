# Research project governance for Codex

This project investigates **Latency Under Load in Wi-Fi 6 and 5G NR-U Coexistence Under Different Channel-Access Mechanisms**. These rules apply to every future task in this repository. They are project policy and remain in force unless the human researcher changes them.

## Ownership and scope

- The human researcher owns the scientific questions, hypotheses, research priorities, and interpretation. Implement the requested scope; do not redefine the central objective or start an unrequested experiment campaign.
- Codex may inspect, implement, test, analyze, document, and propose alternatives. Make scientific assumptions visible and label them; never silently decide scientific meaning.
- Work only inside this project unless the human explicitly authorizes another path. Do not inspect, reuse, or alter unrelated simulator installations or projects.
- Preserve all prior missions, source snapshots, patches, raw data, logs, and derived results. Do not overwrite raw outputs; use a new filename or run-specific directory for every execution. Never use destructive cleanup of earlier research artifacts.

## Mandatory mission start record

Before implementation, create or update the mission report under `docs/missions/` using `templates/MISSION-TEMPLATE.md`. Record:

1. Mission identity/status, objective, scope, research rationale, requirements, and acceptance criteria.
2. Relevant current architecture and affected source/configuration/data components.
3. Planned verification and evidence to preserve.
4. Known dependencies, versions, risks, and non-goals.

For small follow-up tasks, this may be a concise report, but these elements remain mandatory. Do useful read-only investigation while clarifying ambiguity. Do not proceed beyond the human-authorized scientific scope.

## Mandatory documentation policy

Every mission must:

1. Begin with a documented objective, scope, rationale, and acceptance criteria.
2. Identify relevant existing architecture and affected components.
3. Explain significant implementation decisions and why considered alternatives were accepted or rejected. Distinguish contemporary rationale from retrospective inference.
4. Document every source modification, its purpose, effect, and reproducible patch.
5. Record dependencies, exact versions/revisions, configuration, commands, random seeds/runs, and reproduction requirements.
6. Explain algorithms, simulator models, statistics, and measurement procedures, including boundaries and assumptions.
7. Add or revise GitHub-compatible Mermaid diagrams when architecture, data flow, algorithms, topology, or experimental workflow changes. Explain diagrams in prose and label conceptual diagrams.
8. Record all experiments, raw outputs, configuration, seed/run, assumptions, limitations, and validation. Preserve each failed execution's complete log under a unique path before retrying.
9. Explain unexpected findings, failures, debugging choices, fixes, and unresolved issues. Do not erase a failed run's diagnostic evidence.
10. Update relevant existing Markdown documentation instead of creating contradictory parallel narratives. Use links to a canonical detailed document when avoiding necessary repetition.
11. Maintain chronological mission history and update `docs/MISSIONS.md` and root `README.md` links/status.
12. Clearly label statements as source-verified, executed/observed, interpretation, hypothesis, planned work, or unverified assumption. Link claims to evidence.

## Scientific integrity

- Never fabricate results, configurations, source behavior, citations, or validation.
- Do not call a feature standards-compliant merely because it has a standards-related name. Verify implementation and state the limit of that verification.
- Do not present a smoke test as statistically established evidence. Never invent confidence intervals or explanations for observed differences.
- Preserve original raw data independently from analysis. Do not edit past raw records to strengthen a result.
- Distinguish configured/offered load from achieved throughput; distinguish simulation validity from real-world deployment validity.
- Include packet loss/nonreceipt with latency distributions; explain censoring, missingness, and whether quantiles are received-only.
- Keep human ownership of interpretation and the central research question explicit.

## GitHub publication requirement

- After each mission passes the completion gate, create a documented Git commit containing the mission implementation, reports, patches, configurations, and appropriate validated outputs.
- Push the completed commit to the repository's `main` branch unless the human explicitly instructs otherwise.
- Before committing, audit staged paths, file sizes, credentials/secrets, generated binaries, and third-party source trees. Respect `.gitignore`; stage only intended research artifacts.
- Inspect remote history first. Preserve existing commits and reconcile by a normal fast-forward-compatible merge/rebase. Never force-push, delete remote history, change branches as a workaround, or overwrite unrelated remote files. If safe reconciliation is not possible, report the mission as incomplete and explain the blocker.
- Record commit SHA, push status, remote URL, and included files in the mission report and audit. Never include credentials or authentication material in the repository.

## Technical and storage practice

- Inspect relevant project source/config/log/output before claiming behavior.
- Prefer targeted incremental changes/builds; avoid rebuilding or duplicating artifacts unless needed and justify any rebuild.
- Save all source changes as reproducible patches under `patches/`; update `manifests/` when versions/revisions or dependencies change.
- Record all command lines and effective defaults, not just explicit CLI flags.
- Store immutable raw run outputs under unique `results/<mission-or-run-id>/` locations or distinct filenames. Store scripts and configurations alongside documented outputs.
- Check available disk space before substantial builds/runs. Do not delete previous artifacts to make room without explicit authorization.
- Do not change protocol behavior unless explicitly asked. Any authorized protocol change requires separate decision and validation records.

## Mandatory mission completion gate

A mission is **INCOMPLETE** until all applicable items are done:

- Implementation is completed or the technical blocker is established with evidence.
- Appropriate build/test/simulation verification has run and its full log is preserved. If verification cannot run, document why and state the exact limit.
- Raw results, configurations, patches, manifests, and logs are preserved without overwriting earlier outputs.
- The mission report and relevant architecture/methodology docs are updated.
- Required Mermaid diagrams are added or revised.
- Reproduction commands, versions, seeds, run IDs, dependencies, and parameters are recorded.
- `README.md` and `docs/MISSIONS.md` index/status are updated.
- `docs/DOCUMENTATION-AUDIT.md` is updated with link/claim checks and unverified details.
- Remaining limitations, uncertainties, and unresolved questions are disclosed.
- Mission report's documentation checklist is complete.

If code works but any required documentation item remains unfinished, report status **INCOMPLETE**. Do not imply mission completion merely because a simulation exited successfully.

## Required mission workflow diagram

All future reports must include or reference the current mission lifecycle diagram from `docs/missions/mission-2-5-documentation.md`: plan and document → inspect architecture → implement → verify → preserve evidence → update docs/index/audit → completion gate. If that workflow changes, update the diagram and this policy together.

## Documentation navigation

Root `README.md` is the navigation hub. Keep architecture docs under `docs/architecture/`, methodology under `docs/methodology/`, reports under `docs/missions/`, decision records under `docs/decisions/`, and reusable report templates under `templates/`. Update links rather than duplicating contradictory details.
