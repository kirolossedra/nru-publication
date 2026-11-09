# Mission 2 — Per-packet latency instrumentation

**Status:** Complete for instrumentation and one default baseline. The full offered-load campaign has not started.

## Objective and motivation

The Mission 1 SQLite E2E table contained only per-flow means and jitter. Tail latency requires packet-level timestamps. The task added independent per-packet records for NR and Wi-Fi while retaining original SQLite statistics and avoiding any changes to MAC/PHY protocol behavior.

## Implementation

Modified `source/ns-3-dev/contrib/nr-u/examples/cttc-nr-wifi-interference.cc` to:

1. Connect each existing OnOff source's `TxWithSeqTsSize` trace to `LatencyTx`.
2. Bind a technology and flow ID to each source and corresponding PacketSink based on example installation metadata.
3. Use `SeqTsSizeHeader` sequence/timestamp as packet identity and source application TX time.
4. On `PacketSink::RxWithSeqTsSize`, record `Simulator::Now()` for the matching key.
5. Write one CSV row per transmitted application packet with technology, flow ID, sequence ID, TX/RX simulation timestamps, latency, status, and duplicate count.
6. Write a validation sidecar with TX/RX/nonreceipt/duplicate/unmatched counts.

The first receiver matching experiment used peer endpoints and produced unmatched receptions. That run and evidence were preserved in the earlier `logs/baseline-instrumented.log` only until rerun; the file was overwritten by the corrected successful rerun, so the initial mismatch diagnostic itself is not retained in a separate log. The correction binds identity directly to sink install metadata. This is a documentation gap in failure evidence; future missions must preserve each failed run log under a distinct name per AGENTS.md.

The source-only changes are preserved in [`per-packet-latency.patch`](../../patches/per-packet-latency.patch). The executable has `--latencyCsv`; default path is `../../results/per-packet-latency.csv` relative to `source/ns-3-dev`. The CSV schema and measurement semantics are detailed in [latency methodology](../methodology/latency-instrumentation.md).

## Analyzer and outputs

[`scripts/analyze_latency.py`](../../scripts/analyze_latency.py) validates unique TX identities, receive status consistency, nonnegative observed latency, and received count not exceeding TX count. It computes per-technology received-packet mean/median/P95/P99/P99.9, mean absolute successive packet delay variation per flow, stop-time nonreceipt ratio, and configurable deadline-violation ratios. It produces a histogram and ECDF. NumPy and Matplotlib were available in the host Python environment (versions were not recorded at installation time).

## Verification evidence

Incremental build log: `logs/build-latency-instrumentation.log`. Successful run log: `logs/baseline-instrumented.log`. Raw CSV and validation sidecar are `results/per-packet-latency.csv` and `.validation.txt`.

The baseline recorded 62 NR TX, 62 Wi-Fi TX, and 124 unique receives; zero nonreceipts by stop, duplicate receives, or unmatched receives. Analysis result: NR mean 3377.647 µs; Wi-Fi mean 172.791 µs. The same CSV summary contains medians/tails/jitter and deadline ratios. These are preliminary, single-run smoke-test measurements, not statistically established findings; n=62 per technology does not substantiate a stable P99.9.

The Mission 1 and instrumented SQLite E2E rows were compared for technology, throughput, TX/RX bytes, mean latency/jitter, seed, and run. The values matched exactly. Mission 1's preserved SQLite file `results/baseline.db` was not overwritten; the latest run's database is separately generated at the source-tree root.

## Measurement boundary and limitations

TX is the application source trace immediately before UDP socket send; RX is the sink application trace after lower-layer delivery. The measure includes access/queueing and stack/network delay together and is not MAC channel-access latency. Nonreceipt at simulation stop may be packet loss or still-in-flight work; the trace does not identify cause. Percentiles are computed for received packets and must be read with packet loss/deadline violations. Analysis definitions and limitations are in [latency instrumentation](../methodology/latency-instrumentation.md) and [validity risks](../methodology/measurement-validity.md).

No load sweeps, protocol changes, or Mission 3 work were performed.

### Implementation troubleshooting record

The first instrumentation compile attempt failed because this ns-3.35 `Ipv4Address` API has no `ToString()` member. The code was changed to use its supported `Print(std::ostream&)` API; the incremental target then built successfully. The initial error log was overwritten when the successful build log reused `logs/build-latency-instrumentation.log`, so its full diagnostics are not retained. No packet/protocol behavior was changed by this compatibility correction. The current successful build log is retained; this failure-artifact gap is included in the documentation audit.

For durable comparison evidence, the instrumented SQLite file is preserved as [`results/mission2-instrumented.db`](../../results/mission2-instrumented.db); [`results/mission2-sqlite-comparison.txt`](../../results/mission2-sqlite-comparison.txt) contains the exact query outputs and an empty diff against the untouched Mission 1 database.
