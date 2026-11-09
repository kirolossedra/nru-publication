# D-003 — Measure application-to-application delay using existing SeqTs traces

- **Date:** 2026-11-08
- **Status:** Accepted for baseline instrumentation
- **Context:** Mission 1 only stored E2E mean delay/jitter in SQLite; the research requires packet-level tail analysis.
- **Alternatives:** Instrument PHY TX/RX; instrument MAC enqueue/access grant; use FlowMonitor delay only; use OnOff's sequence/timestamp TX trace and PacketSink's matching RX trace.
- **Selected:** Timestamp at `OnOffApplication::TxWithSeqTsSize` and receive at `PacketSink::RxWithSeqTsSize`, using existing `SeqTsSizeHeader` sequence and creation timestamp.
- **Reasoning:** This gives per-packet source-to-sink application delay using built-in traces without changing protocol mechanisms. This choice defines application E2E latency, not isolated channel-access latency. The contemporary task asked for E2E latency and instructed no protocol changes; the design comparison itself was not originally recorded and this rationale is partly retrospective.
- **Consequences:** Access, queueing, retransmission, propagation, and stack delays are aggregated. TX time is an application send attempt immediately before socket send, not first PHY airtime.
- **Disadvantages:** Does not decompose MAC access delay. Stop-time nonreceipt cannot be reliably classified as a drop versus in-flight packet.
- **Evidence:** `cttc-nr-wifi-interference.cc`, `onoff-application.cc`, `packet-sink.cc`, [`per-packet-latency.csv`](../../results/per-packet-latency.csv), [`PER-PACKET-LATENCY.md`](../methodology/latency-instrumentation.md).
