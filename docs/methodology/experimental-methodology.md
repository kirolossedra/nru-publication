# Experimental methodology

## Research question and scope

The human research question is how latency under increasing offered load changes in Wi-Fi 6/NR-U coexistence under different channel-access mechanisms. Intended outcomes are mean and tail latency, throughput, loss, fairness, and channel-access behavior. Mission 3 conducts a bounded, preliminary load pilot under fixed Wi-Fi 802.11ax and NR Cat 4 gNB LBT; it is not the full campaign or a mechanism comparison.

## Current implemented baseline

The installed example sends downlink UDP from a remote host to one NR UE and one Wi-Fi STA in scenario 0. Each OnOff source is configured with constant rate `nodeRate=500kbps` and `PACKET_SIZE=1000`; the same configured packet size includes the SeqTsSizeHeader packet size used by the application. Applications begin at 0.5 s and stop at 1.5 s; simulation stops at 1.5 s. The active interval is therefore 1.0 s, before accounting for startup behavior. Seed=1, run=0, Wi-Fi 802.11ax at 5 GHz, NR Cat 4 gNB LBT, RLC `RlcUmAlways`, error model `ns3::NrEesmIrT1`. Baseline settings are recorded in [`configs/baseline.conf`](../../configs/baseline.conf).

The constant configured application rate is **offered load**, not achieved throughput. The existing SQLite/FlowMonitor value counts IP bytes received over the configured active interval; the Mission 3 analyzer separately derives application payload rate from uniquely received packet count × 1000 bytes / active interval. OnOff TX count similarly gives a source-trace rate. Do not equate configured rate, source trace rate, IP throughput, payload goodput, or radio occupancy.

## Mission 3 pilot configuration (executed)

The pilot keeps the same scenario 0 endpoints, Wi-Fi 802.11ax, NR gNB Cat 4 LBT, 5.2 GHz center frequency, 20 MHz bandwidth, indoor-office propagation, 1000-byte packets, transmit powers, RLC, and error model fixed. Each enabled technology has one downlink UDP OnOff source at a configured constant rate. Selected configured rates are 500 kbps, 2 Mbps, and 12 Mbps per enabled technology. The pilot uses 10, 5, and 3 independent ns-3 seeds respectively. This unequal replication count targets a descriptive range of sample sizes; it is not a balanced inferential design.

Traffic starts at 0.5 s and source applications stop at 4.0 s, giving a 3.5 s active interval. Packet sinks and the simulator continue until 4.9 s, a 0.9 s drain window. This horizon was selected after a longer execution reached an existing negative scheduling delay in `NrUePhy::EndVarTti` at 5.018928564 s. Stopping at 4.9 s avoids that observed failure but is not a repair or validation of the PHY scheduler. Packets not observed by stop are labeled `not_received_by_stop`; they are conservatively counted as nonreceipt and deadline violations, since the trace cannot tell a loss from a packet still in flight.

For each run, configured rate is recorded alongside OnOff TX packet count converted to an observed source-trace rate (`TX packets × 1000 bytes × 8 / 3.5 s`), received application payload rate (`RX packets × 1000 bytes × 8 / 3.5 s`), FlowMonitor IP received throughput over the 3.5 s active interval, and SQLite channel-occupancy ratio over the example's observation window. These are distinct quantities. Channel occupancy is an existing simulator statistic, not a direct physical measurement. 12 Mbps is merely the largest selected rate that completed calibration; measured occupancy did not establish channel saturation.

The exact parameter set, seeds, and modes are in [`configs/mission3-pilot.json`](../../configs/mission3-pilot.json); the runner stores an effective JSON command record with every raw run. The analysis can choose deadlines with `--deadlines-us`, defaulting to 500, 1000, and 5000 µs.

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

The example creates one UDP OnOff source per destination interface and one PacketSink per access endpoint. `SetConstantRate` configures constant offered rate; it is not a saturated-backlogged source. The Mission 1/2 baseline uses 500 kbps per node and one 1000-byte configured packet size. The Mission 3 source trace shows 0.4983, 1.9977, and 11.9977 Mbps for configured 0.5, 2, and 12 Mbps respectively. With no packet nonreceipt in the primary runs, received application payload rates equal these rates. FlowMonitor IP throughput was 0.5122, 2.0537, and 12.3337 Mbps because its byte accounting is at IP. The analyzer checks OnOff TX/RX packet counts and reports these quantities separately.

## Simulation duration, warm-up, repetitions

The original 1.5 s total duration and 0.5 s traffic start are only the example's smoke-test defaults. They have not been shown to reach steady state and are too short to establish stable tail behavior. The Mission 3 4.9 s horizon and 3.5 s active window provide more observations but likewise have not been shown to reach steady state; its findings are preliminary. The configured rates and packet counts determine sample populations, and P99.9 is reported only for pooled received populations of at least 10,000, a minimum reporting gate rather than a guarantee of precise tail estimation. A future methodology should justify warm-up and measurement windows, ensure offered load and queue state are representative, and quantify how much tail data each run provides. It should predefine independent runs and seeds, retain each raw run, and estimate uncertainty across independent simulation replications rather than treating packets from one run as independent simulation trials.

Seed/run are explicit (1/0 in baseline). For future trials, use a declared seed/run schedule, preserve RNG assignment behavior, and avoid reusing identical streams accidentally across purportedly independent trials. Run count and stopping criteria must be justified before inspecting desired outcomes.

## Statistical approach (planned, not current evidence)


Per-run latency metrics are computed only over received packets. P99.9 is reported only when the pooled condition has at least 10,000 received packets; this is a minimum reporting gate, not a claim that the tail is precise. The analyzer's jitter is mean absolute difference between consecutive received-packet latencies in TX order, per flow, then averaged within run. Deadline violation ratio is `(received packets above threshold + not_received_by_stop packets) / transmitted packets`; the latter are conservatively counted as misses. The analyzer computes descriptive across-seed means, standard deviations, and Student-t 95% intervals for selected run-level metrics. It does not treat packets as independent simulation replications. Tail quantiles use NumPy's default interpolation method. Confidence intervals over three seeds are highly uncertain and do not include model uncertainty. The pilot does not fit a model or infer causality. A future plan should define estimands, independent unit, quantile method, uncertainty, multiplicity handling where relevant, and effect sizes before the campaign. Keep raw measurements and a machine-readable configuration alongside derived outputs.

## Existing outputs and interpretation

SQLite contains example-level summaries and instrumentation; Mission 2 CSV holds per-packet timestamps/status. E2E delay is application source to PacketSink. End-of-run missing packets are censored at stop rather than known drop causes. `docs/methodology/measurement-validity.md` lists required validity checks before publication interpretation.
