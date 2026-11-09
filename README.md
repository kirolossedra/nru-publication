# Latency Under Load in Wi-Fi 6 and 5G NR-U Coexistence

A reproducible ns-3 research environment for studying latency and other network outcomes when Wi-Fi 6 and 5G NR-U share unlicensed spectrum under different channel-access mechanisms.

> Current status: Missions 1 and 2 are implemented and documented. The installed compatibility stack builds, the official NR-U/Wi-Fi coexistence example runs, and application-boundary packet latency is exported to CSV. No load-sweep campaign has started. The single saved baseline is a smoke test, not a scientific finding.

## Motivation and central question

Wi-Fi 6 (IEEE 802.11ax) and NR-U can operate in unlicensed spectrum. Their transmissions may contend for or interfere in the same band, while their channel-access and medium-sharing behavior differ. This project asks:

**How does end-to-end latency, including its tail, change under increasing offered load when Wi-Fi 6 and NR-U coexist using different channel-access mechanisms?**

The intended dependent outcomes are average latency, P95/P99/P99.9, throughput, packet loss, fairness, and channel-access behavior. The human researcher owns scientific hypotheses and interpretation; future experiments must not silently change the question or assumptions.

## Current simulation

The installed official `cttc-nr-wifi-interference` example creates an NR gNB/UE link and a Wi-Fi AP/STA link in a shared 5.2 GHz, 20 MHz spectrum channel with indoor-office propagation. A remote host sends UDP traffic toward both access links. The baseline selects Wi-Fi 802.11ax at 5 GHz and NR gNB Cat 4 LBT. Mission 2 adds source-application TX and sink-application RX traces to produce one record per transmitted packet without replacing the example's SQLite statistics.

The diagrams and implementation details are in [simulator architecture](docs/architecture/simulator.md), [coexistence implementation](docs/architecture/coexistence.md), and [packet/measurement flow](docs/architecture/packet-flow.md).

## Software stack and environment

| Component | Installed version/revision | Role |
|---|---|---|
| ns-3 | 3.35, `ac88b75eac1818c673cf2c939a96ac3005b1f051` | Discrete-event network simulator, core, Internet, spectrum, Wi-Fi |
| 5G-LENA NR | v1.2 line, `fe0a1d2a5fb7d1547e46042041288a684893ba9e` | NR radio access network |
| NR-U extension | `75a45143b1cd382326876a9597e856338673039a` | NR-U channel access/LBT and coexistence example |
| Host | Ubuntu 24.04.3 LTS; GCC toolchain used by build; Python 3.12.3 | Build/runtime environment |

See [commits manifest](manifests/commits.txt) and [Mission 1 report](docs/missions/mission-1-environment.md). Three localized `<cstdint>` include fixes for this legacy source/compiler combination are preserved as [a patch](patches/ns-3.35-gcc-fixed-width-includes.patch). Configure/build commands and logs are documented in [installation status](docs/INSTALL-STATUS.md).

## Reproduction overview

From the project root:

```sh
cd source/ns-3-dev
./waf build -j 4
./waf --run cttc-nr-wifi-interference
cd ../..
python3 scripts/analyze_latency.py results/per-packet-latency.csv --deadlines-us 100,500,1000
```

This uses the saved default baseline (seed 1, run 0, 500 kbps per node, 1.5 s total simulation, applications start at 0.5 s, Cat 4 LBT). The executable writes raw per-packet data to `results/per-packet-latency.csv`; the analysis tool writes summaries and plots under `results/latency-analysis/`. Full procedure and measurement definitions: [latency instrumentation](docs/methodology/latency-instrumentation.md).

## Scenarios and capability status

The example exposes scenario 0 (`SinglePairNodeScenario`) and scenario 1 (`InFrontNodeDistribution`), Wi-Fi `11ac` or `11ax`, NR gNB Cat 2/3/4 LBT and always-on/on-off manager choices, and flags for enabling technologies/doubling technology nodes. Only the default scenario 0, Wi-Fi 11ax, Cat 4 LBT coexistence baseline has been executed here. Do not treat unrun options as empirically verified. Details and source references: [coexistence implementation](docs/architecture/coexistence.md).

Current measurements include throughput and mean delay/jitter in SQLite, plus per-packet source-to-sink application latency, packet nonreceipt by simulation stop, empirical percentiles, absolute successive-packet latency variation, and configurable deadline ratios in CSV analysis. MAC channel-access delay is not derived from end-to-end latency; request-time and channel occupancy traces are separate outputs. Percentiles are conditional on received packets and must be considered with packet loss/deadline violations.

## Mission history

- [Mission 1 — Environment installation](docs/missions/mission-1-environment.md): compatible source stack, compile patch, official coexistence baseline, capabilities and limits.
- [Mission 2 — Per-packet latency](docs/missions/mission-2-latency.md): trace instrumentation, raw CSV, matching/loss validation, analysis and plots.
- [Mission 2.5 — Documentation governance](docs/missions/mission-2-5-documentation.md): this documentation system, audit and permanent AGENTS.md policy.

The [mission history index](docs/MISSIONS.md) is chronological. [Decision records](docs/decisions/README.md) capture engineering and research choices.

## Known limitations

- Upstream describes NR-U/Wi-Fi coexistence as experimental; this simulator model is not proof of standards conformance or real-world deployment performance.
- The baseline is one short run with 62 packets per technology; tail quantiles at this size are unstable and are not generalizable.
- A packet absent at simulation stop may be dropped or still in flight; the current trace cannot distinguish these cases.
- Per-packet percentiles are received-packet conditional; lost packets can mask tail behavior, so also report loss and deadline violation ratio.
- The baseline is downlink UDP only; fairness, offered-load sweeps, repeated-trial inference, and deadline-driven scheduling studies remain future work.
- The current example does not generate an isolated MAC channel-access latency metric.

## Documentation index

- [Documentation audit](docs/DOCUMENTATION-AUDIT.md)
- [Architecture](docs/architecture/README.md)
- [Methodology](docs/methodology/README.md)
- [Mission reports](docs/MISSIONS.md)
- [Decision log](docs/decisions/README.md)
- [Reusable mission template](templates/MISSION-TEMPLATE.md)
- [Permanent agent governance](AGENTS.md)

For a full experimental design, see [experimental methodology](docs/methodology/experimental-methodology.md) and [measurement validity risks](docs/methodology/measurement-validity.md). For project-specific architecture decisions, see the [decision record index](docs/decisions/README.md).

For a fresh workspace, [`scripts/install-environment.sh`](scripts/install-environment.sh) checks out the exact pinned sources, applies the compatibility and latency patches, then configures and builds without installing system packages or replacing an existing `source/` tree. See Mission 1 for host prerequisites.
