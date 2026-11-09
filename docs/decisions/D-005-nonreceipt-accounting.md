# D-005 — Preserve every transmitted ID and account for stop-time nonreceipt

- **Date:** 2026-11-08
- **Status:** Accepted for instrumentation; drop-cause classification remains unresolved
- **Context:** Received-only analysis can omit packets that did not reach the sink and thereby hide loss or deadline misses.
- **Alternatives:** Exclude missing IDs; assign fabricated latency to missing packets; keep a TX-ledger row with no RX latency and report a separate loss/deadline denominator.
- **Selected:** Emit one CSV row per TX. Leave RX/latency blank for packets with no RX by simulation stop; count those as nonreceived and as deadline violations for every deadline threshold.
- **Reasoning:** This retains packet accounting without inventing latency. A current simulation-stop trace cannot prove whether a missing packet is permanently dropped or merely in flight; this treatment is conservative for deadline accounting.
- **Consequences:** Latency quantiles remain received-packet conditional; analyses must pair them with nonreceipt/loss and deadline ratios. Future study may require drain time and drop-cause instrumentation.
- **Disadvantages:** It does not give a definitive network packet-loss cause or uncensored latency distribution when packets are missing.
- **Evidence:** `LatencyPacket`, `LatencyRx`, `WriteLatencyCsv`, analyzer and validation sidecar; [measurement validity](../methodology/measurement-validity.md).
