# D-004 — Preserve SQLite and export raw packet measurements to CSV

- **Date:** 2026-11-08
- **Status:** Accepted
- **Context:** Existing NR-U example writes SQLite summaries; research needs raw packet-level values. Mission requirements explicitly required CSV without replacing SQLite.
- **Alternatives:** Replace SQLite schema; store individual packet events in SQLite; add a separate raw CSV output while retaining the existing database.
- **Selected:** Keep `SqliteOutputManager` behavior and add one CSV row per source TX with receive fields or explicit nonreceipt status.
- **Reasoning:** This satisfies the explicit requirement while retaining existing summary output and keeping raw rows directly inspectable. No benchmark of storage formats was conducted.
- **Consequences:** CSV is an independent raw artifact; analysis script derives summaries and figures from it. Example-generated SQLite is still written in ns-3 source tree working directory, so copy/store raw DB carefully for each future run.
- **Disadvantages:** CSV and SQLite outputs need coordinated run metadata; current CSV has no top-level run/config columns, so preserve `configs/` and separate files/run directories.
- **Evidence:** `cttc-nr-wifi-interference.cc`, [`results/per-packet-latency.csv`](../../results/per-packet-latency.csv), `results/baseline.db`, instrumented SQLite output DB under `source/ns-3-dev/`.
