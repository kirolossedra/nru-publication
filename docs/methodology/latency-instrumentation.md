# Per-packet latency measurement

## Timestamp boundary and meaning

The source timestamp is `SeqTsSizeHeader::GetTs()` in the existing `OnOffApplication::TxWithSeqTsSize` callback. ns-3's OnOff implementation sets the sequence, size, and current simulation timestamp before it invokes this trace, then serializes the header and sends the packet through its UDP socket. This is the application TX boundary (packet creation/send attempt), not the timestamp of first PHY transmission.

The receive timestamp is `Simulator::Now()` in the receiver's `PacketSink::RxWithSeqTsSize` callback. It is taken after lower layers have delivered the UDP datagram and PacketSink has recognized the sequence/timestamp header. The difference is source-application-to-sink-application end-to-end latency in ns-3 simulation time.

Included: application and stack queueing, routing, NR/Wi-Fi MAC contention/access, transmissions/retransmissions represented by the model, propagation, and receive-stack processing up to PacketSink's trace. Excluded: application response time after PacketSink, real wall-clock runtime, and an isolated MAC channel-access duration. An NR/Wi-Fi channel-access delay must be measured at request/grant or MAC enqueue/transmit events; subtracting an approximate channel-request statistic from an E2E sample would not be valid.

## Identity and matching

CSV packet identity is `(technology, flow_id, packet_id)`. `packet_id` is `SeqTsSizeHeader::GetSeq()` scoped to each OnOff application. `flow_id` is assigned per access technology/destination application. The TX callback inserts one ledger record; a repeated TX sequence for the same key aborts rather than silently overwriting a record. Each PacketSink trace is bound to its known technology and flow ID using the example's sink installation metadata. RX must match the full tuple.

The first matching RX sets receive time. A duplicate matching RX increments a duplicate counter and does not create another latency sample. An RX with no matching TX increments unmatched count. The CSV contains one row per TX, not one row per RX.

## CSV schema

`technology, flow_id, packet_id, tx_timestamp_ns, rx_timestamp_ns, latency_ns, status, duplicate_rx_count`

Times are integer ns of simulation time. `latency_ns = rx_timestamp_ns - tx_timestamp_ns`. For nonreceipts, receive time and latency are empty and status is `not_received_by_stop`. CSV raw data is preserved independently from processed summaries.

## Nonreceipt and loss treatment

Packets with no matching receive at simulator stop remain in the ledger. This avoids calculating latency only from whichever packet happened to arrive without exposing the loss count. The analyzer reports `not_received_by_stop / transmitted` as packet-loss ratio and includes every such packet as a deadline violation for every configured threshold. These are end-of-run nonreceipts, not proven PHY/MAC drops: a packet may be queued or in flight when simulation ends. Increase duration or add drain time in a separately documented methodology before interpreting them as confirmed losses.

Latency mean/median/percentiles and plots are conditional on received packets; the current CSV does not assign invented latency to missing packets. Thus a low conditional tail alone can be misleading if high-delay packets are lost. Report it together with packet-loss and deadline-violation ratios, and consider latency-with-censoring methods for larger studies. The baseline has zero nonreceipts, so this censoring caveat does not change its calculated latency values.

## Analysis definitions

`scripts/analyze_latency.py` validates duplicate TX keys, receive/status consistency, nonnegative observed latency, and received count not exceeding TX count. Per technology:

- Mean and median use received latency values in µs.
- P95, P99, P99.9 use NumPy `percentile` with its default linear interpolation on received values.
- Jitter is the mean absolute difference between successive received-packet latency values within each flow, ordered by TX timestamp. It is absolute inter-packet delay variation, not Wi-Fi/NR MAC jitter or the same as every RFC jitter estimator.
- Packet-loss ratio is `not_received_by_stop / tx_packets`.
- Deadline violation ratio at threshold `D` is `(not_received_by_stop + count(received latency > D)) / tx_packets`. Equality is not a violation. Thresholds are CLI arguments in microseconds.

Plots show received packet latencies only. The latency histogram and empirical CDF are descriptive figures, not confidence intervals. With 62 receptions per technology, the extreme percentiles are particularly sample-size-sensitive.

## Reproduction

```sh
cd source/ns-3-dev
./waf build -j 4
./waf --run cttc-nr-wifi-interference
cd ../..
python3 scripts/analyze_latency.py results/per-packet-latency.csv --deadlines-us 100,500,1000
```

Options/defaults: `--latencyCsv=../../results/per-packet-latency.csv` in the simulation binary's working directory; seed 1, run 0, Wi-Fi 11ax, Cat 4 gNB LBT, 500 kbps per node, scenario 0, 1.5 s total with apps from 0.5 s. The analysis creates `results/latency-analysis/`; change `--out-dir` to write elsewhere. Use `--deadlines-us 50,250,750` to change deadline thresholds. Do not run this command over a raw CSV you need to preserve without first choosing a new `--latencyCsv` path.

## Artifacts

See [raw records](../../results/per-packet-latency.csv), [validation counts](../../results/per-packet-latency.csv.validation.txt), [summary](../../results/latency-analysis/latency-summary.csv), [histogram](../../results/latency-analysis/latency-distribution.png), [ECDF](../../results/latency-analysis/latency-ecdf.png), and [Mission 2 report](../missions/mission-2-latency.md).
