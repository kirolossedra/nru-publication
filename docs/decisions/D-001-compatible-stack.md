# D-001 — Use the documented compatible legacy NR-U stack

- **Date:** 2026-11-08
- **Status:** Accepted for the current project environment
- **Context:** The task required a genuine NR-U/Wi-Fi coexistence example. The standalone NR-U repository README specified ns-3.35, 5G-LENA branch `5g-lena-v1.2.y`, and NR-U master.
- **Alternatives:** Use a newer integrated 5G-LENA NR release; attempt to port standalone NR-U; use generic cross-technology interference without NR-U LBT.
- **Selected:** Independently check out the three revisions specified by the NR-U repository and run its official coexistence example.
- **Reasoning:** The recorded Mission 1 instruction explicitly prioritized verified compatibility over newer versions; the NR-U README gave the stack and example. This is the documented reason. No separate compatibility comparison matrix was created at selection time.
- **Consequences:** The work uses a legacy codebase and requires a small compiler compatibility patch on Ubuntu 24.04. Upstream characterizes coexistence as experimental. The baseline is genuine NR-U access plus Wi-Fi in the selected source implementation.
- **Disadvantages:** Legacy source and tooling may encounter modern compiler/Python incompatibilities; functionality is not proof of standards compliance or deployment validity.
- **Evidence:** [`manifests/commits.txt`](../../manifests/commits.txt), `source/ns-3-dev/contrib/nr-u/README.md`, `logs/configure.log`, `logs/build-resume-1.log`, `logs/baseline.log`.
