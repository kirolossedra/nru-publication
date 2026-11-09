# Mission 4 — O-RAN project migration and legacy environment retirement

**Status:** COMPLETE. **Date:** 2026-11-09.

## Objective and scope

Pause active NR-U work, preserve this repository as a complete historical archive, create a distinct O-RAN research repository, select the upstream-supported modern version combination, and retire only the legacy simulator source/build tree owned by this project. Acceptance requires both repositories updated and pushed safely; exact source versions and cleanup scope documented; unrelated research and shared dependencies untouched. No new simulator installation, build, or experiment is in scope.

## Research rationale

The active question is transitioning to 5G RAN resource allocation and O-RAN-based control. A separate repository and source boundary avoid contaminating the modern stack with ns-3.35/NR v1.2/NR-U APIs and local compiler patches while leaving prior experiments reproducible through their GitHub archive.

## Audit and ownership evidence

Before transition, this repository's `main` was clean and matched origin at `997641ad294fab5040b5b5c556a40ecd6ba91879`. Its published history contains Missions 1, 2, 2.5, and 3, tracked patches, documentation, and selected validated results. Local simulator source under `source/ns-3-dev` was audited as this project's ignored, owned installation: ns-3 3.35 at `ac88b75eac1818c673cf2c939a96ac3005b1f051`; NR v1.2 line at `fe0a1d2a5fb7d1547e46042041288a684893ba9e`; NR-U extension at `75a45143b1cd382326876a9597e856338673039a`. It occupied about 3.2 GB source plus 2.9 GB build. Legacy source modifications are preserved as tracked patches; one root database was hash-identical to the archived Mission 2 result. Mission 3 raw data are retained in the parent project. Two additional ns-3 directories belonging to the separate `other-research/Research/OtherP/NR-U` project are out of scope and retained. System packages have shared/uncertain ownership and are retained.

## New project and selected stack

The independent [O-RAN repository](https://github.com/kirolossedra/oran-publication) contains research governance, objective/methodology, architecture and scenario diagrams, version manifest, compatibility/install documentation, decision records, template, and empty data/script directory guides. Its selected pins are ns-3.48, 5G-LENA v5.1, ns3-ai `main`, ib-ORAN `main`, Python 3.11+. Upstream-tested pairing is documented; the stack was not installed or built. See the new project's [compatibility analysis](https://github.com/kirolossedra/oran-publication/blob/main/docs/COMPATIBILITY.md).

## Changes and decisions

- Old README marks this project paused and links to the new active repository while retaining all historical technical content.
- Parent `.gitignore` excludes the nested O-RAN repository from historical tracking.
- New project uses its own Git history and ignores future simulator/build artifacts.
- Do not reuse legacy patches; do not remove other-project simulator trees or shared packages.
- Dated reasoning and compatibility evidence are recorded in the new repository's decision log; the choice of separate repositories and pins is partly retrospective inference from the ownership and official compatibility records.

## Reproduction and verification

The archived NR-U environment remains documented and versioned in GitHub; its local simulator tree has been retired. The O-RAN project is reproducible as documentation at its published commit; simulator reproduction is not yet applicable. The new public repository's initial `main` commit is `4952d832af2d233a6c1ad5adef3e96a59256ef73`. The old archive migration commit and final remote SHAs are recorded in the completion report and can be obtained with `git rev-parse origin/main` in each repository.

Retirement command used a Python guard that required the exact canonical, non-symlink directory `/home/kiro/other-files/self-research/source/ns-3-dev`, then removed that tree only. Before removal it measured 3.2 GB for the tree and 17 GiB available on the filesystem; after removal, 20 GiB was available. Mission 3 local raw data remain 9.8 MB under `results/mission3`. The now-empty legacy `source/` parent and all tracked research files remain. No unrelated directories or system packages were changed.

Publication audit staged only `.gitignore`, README, mission index, this report, and the audit update. Remote `main` was checked at `997641ad294fab5040b5b5c556a40ecd6ba91879` immediately before push; no force-push or branch switch was used. The commit was pushed by a normal fast-forward. The O-RAN repository is public at `https://github.com/kirolossedra/oran-publication`; its initial source/documentation commit is above. The O-RAN repository contains no simulator checkout, binary, large output, or copied legacy patch.

## Limitations and unresolved questions

No O-RAN source has been fetched, and no modern build/run has been validated. Host Boost/pybind11 versions are below the upstream minimum; Python 3.11 and protobuf development tools were absent. Mobility capability exists in the upstream ns-3/NR ecosystem but use in the selected ib-ORAN scenario remains to be checked. These must be resolved in a separately scoped installation mission.

## Completion checklist

- [x] Historical research and exact project-owned source tree verified before retirement
- [x] Separate O-RAN repository scaffold, documentation, and version manifest created
- [x] Official compatibility evidence and unverified installation status recorded
- [x] Historical archive README, mission index, and audit updated without removing history
- [x] Only the owned legacy checkout/build tree removed; other project installs and shared packages retained
- [x] Relative links, JSON manifest, Mermaid fences, staged file sizes, and source-tree/credential scope checked
- [x] New O-RAN public repository and historical archive pushed to `main`; remote SHAs/status verified
- [x] No Mission 3/O-RAN experiments or O-RAN build performed
