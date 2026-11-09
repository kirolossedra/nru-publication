# Per-packet application latency instrumentation

## Measurement boundary

The source timestamp comes from the `SeqTsSizeHeader` emitted by the example's existing `OnOffApplication::TxWithSeqTsSize` trace, just before the packet is sent to its UDP socket. The receive timestamp is `Simulator::Now()` in `PacketSink::RxWithSeqTsSize`, after UDP delivery and packet-sink header processing. Both use ns-3 simulation time. Their difference is application-level source-to-sink end-to-end delay for a received packet.

This boundary includes queueing, NR/Wi-Fi MAC access, retransmissions, PHY transmission, and intervening network-stack delay together. It does not isolate MAC channel-access delay; `channel_request_time` in the existing SQLite output is separate instrumentation and is not subtracted from this end-to-end delay. Instrumentation adds only trace callbacks and output I/O after simulation; it changes no protocol attributes or access procedures.

Each row's identity is `(technology, flow_id, packet_id)`. The packet ID is the `SeqTsSizeHeader` sequence number scoped to the particular application flow. TX rows are created once; an RX must match an existing tuple. Duplicate receives increment `duplicate_rx_count` and do not add samples. Unmatched RXs are counted in the validation sidecar. A transmitted packet without an RX at simulator stop remains in the CSV with empty receive/latency fields and `not_received_by_stop` status. This is conservative end-of-run accounting: a packet still in flight at stop is indistinguishable from a dropped packet from these traces alone.

Latency percentiles and distribution plots are conditional on packets received by the application sink. Always interpret them together with `not_received_by_stop`, packet-loss ratio, and deadline-violation ratio; lost packets are counted as deadline violations at every configured deadline. Do not interpret the stop-time nonreceipt count as a confirmed PHY/MAC drop cause.

## Files and validation

- `source/ns-3-dev/contrib/nr-u/examples/cttc-nr-wifi-interference.cc`: trace instrumentation and raw CSV writer.
- `patches/per-packet-latency.patch`: reproducible source diff against the Mission 1 code state.
- `results/per-packet-latency.csv`: one row per transmitted packet.
- `results/per-packet-latency.csv.validation.txt`: TX, unique RX, nonreceipt, duplicate, and unmatched counts.
- `scripts/analyze_latency.py`: standard CSV analysis; requires NumPy and Matplotlib.
- `results/latency-analysis/latency-summary.csv`, `latency-distribution.png`, and `latency-ecdf.png`: derived results and plots.
- `logs/build-latency-instrumentation.log`, `logs/baseline-instrumented.log`: build and run logs.

Baseline validation: 124 transmitted IDs (62 NR, 62 Wi-Fi), all 124 uniquely received, no missing-at-stop packets, duplicate receives, or unmatched receives. The baseline E2E SQLite rows (throughput, bytes, mean latency/jitter, seed/run) match Mission 1 exactly; this is a check that the added traces did not change observed protocol/statistics behavior. The original Mission 1 database `results/baseline.db` remains untouched.

## Analysis definitions

- Mean, median, P95, P99, and P99.9: empirical statistics of received packet latencies in microseconds, independently per technology. Percentile implementation is NumPy's default linear interpolation.
- Jitter: mean absolute difference between consecutive received-packet latencies within each flow, ordered by TX timestamp (absolute inter-packet delay variation).
- Packet loss ratio: `not_received_by_stop / transmitted`.
- Deadline violation ratio: `(not_received_by_stop + received packets with latency > deadline) / transmitted`. Deadline comparison is strict `>`.

## Reproduction

From the project root, first build incrementally and run the same default 802.11ax / NR Cat 4 LBT baseline:

```sh
cd source/ns-3-dev
./waf build -j 4
./waf --run cttc-nr-wifi-interference
cd ../..
python3 scripts/analyze_latency.py results/per-packet-latency.csv \
  --deadlines-us 100,500,1000
```

By default the example writes to `../../results/per-packet-latency.csv` relative to `source/ns-3-dev`. Override with `--command-template` if a different output path is needed; the executable accepts `--latencyCsv=PATH`. Configure other deadlines in microseconds, for example `--deadlines-us 50,250,750`.

Seed, run ID, load, channel access, and scenario are unchanged from the Mission 1 baseline (seed 1, run ID 0, default 500 kbps per node, Cat 4 LBT, scenario 0). The full-load campaign remains unstarted.

For system-level research context, architecture diagrams, detailed validity risks, and mission governance, see the [root README](../README.md), [architecture guide](architecture/README.md), [measurement-validity table](methodology/measurement-validity.md), and [Mission 2 report](missions/mission-2-latency.md). The source baseline and exact stack revisions are indexed in the [Mission 1 report](missions/mission-1-environment.md).
