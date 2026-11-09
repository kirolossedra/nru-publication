# Experimental methodology

## Research question and scope

The human research question is how latency under increasing offered load changes in Wi-Fi 6/NR-U coexistence under different channel-access mechanisms. Intended outcomes are mean and tail latency, throughput, loss, fairness, and channel-access behavior. This file separates the current baseline from a proposed future campaign; Mission 3 has not started.

## Current implemented baseline

The installed example sends downlink UDP from a remote host to one NR UE and one Wi-Fi STA in scenario 0. Each OnOff source is configured with constant rate `nodeRate=500kbps` and `PACKET_SIZE=1000`; the same configured packet size includes the SeqTsSizeHeader packet size used by the application. Applications begin at 0.5 s and stop at 1.5 s; simulation stops at 1.5 s. The active interval is therefore 1.0 s, before accounting for startup behavior. Seed=1, run=0, Wi-Fi 802.11ax at 5 GHz, NR Cat 4 gNB LBT, RLC `RlcUmAlways`, error model `ns3::NrEesmIrT1`. Baseline settings are recorded in [`configs/baseline.conf`](../../configs/baseline.conf).

The constant configured application rate is **offered load**, not achieved throughput. Achieved throughput is calculated from bytes received by FlowMonitor over the active interval. Do not equate 500 kbps with measured application goodput or radio utilization.

## Experimental variables

### Planned independent variables (not yet swept)

- Offered rate per technology / number of sources.
- NR gNB channel-access manager (Cat 2, Cat 3, Cat 4; potentially selected additional managers with a clear scientific reason).
- Wi-Fi standard/configuration and Wi-Fi contention parameters, only when needed by the research question.
- Number and placement of stations/UEs and the selected built-in scenario.
- Potentially channel-access thresholds and simulation channel conditions as controlled sensitivity variables.

Do not change multiple variables without recording the full configuration and the reason. The central research objective remains unchanged unless the human researcher directs otherwise.

### Dependent variables

- Per-packet application E2E latency and mean/median/P95/P99/P99.9.
- Throughput/goodput, TX/RX counts, packet nonreceipt/loss, deadline violations.
- Fairness metric, to be selected and justified before use (for example, a defined Jain index over per-flow throughputs; not currently implemented).
- Channel occupancy, request timing, simultaneous transmission, MAC failure callbacks, and other channel-access indicators that the source actually records.

### Controlled variables

For a valid access-mechanism comparison, hold constant Wi-Fi mode, frequency/bandwidth, node positions, propagation/channel models, packet size, traffic direction, offered load, simulation start/stop, NR scheduler/error model/RLC, and randomization policy unless one is the independent variable. Save every effective configuration, including defaults that may not appear on the command line.

## Traffic and offered load

The example creates one UDP OnOff source per destination interface and one PacketSink per access endpoint. `SetConstantRate` configures constant offered rate; it is not a saturated-backlogged source. The Mission 1/2 baseline uses 500 kbps per node and one 1000-byte configured packet size. Any load sweep must confirm actual OnOff packet generation, sink receives, active duration, and whether the configured rate includes all relevant headers before interpreting load. Throughput is measured separately from offered load.

## Simulation duration, warm-up, repetitions

Current 1.5 s total duration and 0.5 s traffic start are only the example's smoke-test defaults. They have not been shown to reach steady state and are too short to establish stable tail behavior. A future methodology should justify warm-up and measurement windows, ensure offered load and queue state are representative, and quantify how much tail data each run provides. It should predefine independent runs and seeds, retain each raw run, and estimate uncertainty across independent simulation replications rather than treating packets from one run as independent simulation trials.

Seed/run are explicit (1/0 in baseline). For future trials, use a declared seed/run schedule, preserve RNG assignment behavior, and avoid reusing identical streams accidentally across purportedly independent trials. Run count and stopping criteria must be justified before inspecting desired outcomes.

## Statistical approach (planned, not current evidence)

The current script computes empirical summaries from received packets but does not compute confidence intervals, compare mechanisms, fit a model, or infer causality. A future analysis plan should define estimands, independent unit (typically simulation run), tail quantile method, confidence interval or bootstrap strategy, multiple-comparison handling where relevant, and effect sizes before the campaign. Per-packet quantiles within one run are descriptive and do not alone quantify between-run uncertainty. Keep raw data and a machine-readable configuration alongside every derived output.

## Existing outputs and interpretation

SQLite contains example-level summaries and instrumentation; Mission 2 CSV holds per-packet timestamps/status. E2E delay is application source to PacketSink. End-of-run missing packets are censored at stop rather than known drop causes. `docs/methodology/measurement-validity.md` lists required validity checks before publication interpretation.
