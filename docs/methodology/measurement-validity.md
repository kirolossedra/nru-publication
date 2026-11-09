# Measurement validity and risks

This inventory separates observed implementation behavior from unresolved validity questions. The baseline establishes execution and data plumbing, not scientific validation.

| Risk | Current implication | Validation/mitigation before inference |
|---|---|---|
| Short baseline (1.5 s total, 1 s active traffic) | Only 62 packets per technology were received; tail quantiles are unstable and steady state is unestablished. | Choose duration from convergence/sample-size analysis; separate warm-up and measurement intervals; compare longer windows. |
| Percentiles are conditional on receive | Lost high-latency packets can make received-only P95/P99 look lower. | Report nonreceipts/loss and deadline violations with every latency summary; consider censored-latency methods and extend/drain simulation. |
| Stop-time censoring | `not_received_by_stop` may be a dropped packet or still in flight/queued. | Add a documented drain period after sources stop; use network/MAC drop traces to classify causes without assigning fabricated latency. |
| Offered-load versus achieved-throughput distinction | A configured 500 kbps rate is not evidence that the receiver achieves 500 kbps. | Verify actual source TX bytes/rate and sink RX goodput over clearly defined intervals for each run. |
| Source measurement boundary | Timestamp is OnOff app TX trace before socket send; RX is PacketSink app trace. It includes access/queueing but not a pure MAC delay. | Keep boundary fixed; validate callback ordering and header timestamp semantics; add separate MAC request/grant tracing only as a separate metric. |
| Flow classification | Example maps destination IPv4 space to technology; sink metadata is bound during helper installation. | Assert route/destination mapping for each scenario; include flow table/config with experiment; test each supported topology before use. |
| Sequence number scope | Packet ID is a 32-bit per-OnOff sequence, scoped by technology and flow ID. | Preserve flow IDs; check wrap for long runs; add a wider experiment/run identifier if combining CSV files. |
| Duplicate/lost packet instrumentation | Current baseline has no duplicates and no missing packets, so duplicate/drop branches are source-reviewed but not exercised by this run. | Add focused synthetic tests or controlled fault/drop scenario in a separate validation mission; preserve that run and verify counts. |
| Shared spectrum/model assumptions | Same channel object and 5.2 GHz configuration are present, but this does not prove calibration or standards compliance. | Review propagation/interference implementation, verify cross-technology energy sensing, compare against published validation/reference scenarios, and state limits. |
| Experimental NR-U coexistence feature | Upstream identifies coexistence as experimental; behavior depends on specific legacy commits. | Cite exact revisions; inspect relevant code; perform sensitivity and external validation before standards claims. |
| Run-level statistical uncertainty | Packets within one simulation share state and are not independent replications. | Use multiple independently seeded runs; analyze across-run estimates and quantify uncertainty. |
| Instrumentation overhead | Trace callbacks add work and CSV I/O occurs after simulation. They should not affect simulated time, but actual event ordering must remain the same. | Mission 2 found SQLite E2E rows identical to Mission 1; preserve this comparison and consider deterministic paired baseline checks. |
| Baseline metric discrepancy/resolution | Historical SQLite baseline and per-packet baseline have different measurement pipelines and rounding. | Keep raw evidence and compare the same SQLite columns for behavior-preservation; do not claim exact equality between different latency measurement boundaries. |
| Model-to-deployment gap | Simulated devices, ideal rate manager, propagation, queues, and LBT behavior do not equal production hardware. | Treat simulator findings as model-conditional; validate with testbed evidence if making deployment claims. |

## Current evidence

- Build logs show successful compilation after three include-only compatibility changes.
- Instrumented execution exits 0 and has 124 TX/124 unique RX, zero unmatched/duplicate/nonreceived records at simulation stop.
- Mission 1 SQLite database remains preserved at `results/baseline.db`; instrumented SQLite output is in the source tree-generated DB. Comparisons are documented in Mission 2 report.
- There is no current validation of overload behavior, Cat 2/Cat 3 comparisons, Wi-Fi interoperability on hardware, statistical confidence, fairness, or standards conformance.
