# Latency Under Load in Wi-Fi 6 and 5G NR-U Coexistence

A historical, reproducible ns-3 research environment for studying latency and other network outcomes when Wi-Fi 6 and 5G NR-U share unlicensed spectrum under different channel-access mechanisms.

> **Archive status:** NR-U work is paused. This repository preserves the completed Missions 1–3, their source patches, documentation, and historical results. Active research has moved to the separate [O-RAN publication repository](https://github.com/kirolossedra/oran-publication). No history or technical records have been removed. The historical stack documented below is not used by the O-RAN project.

The Mission 3 pilot results remain preliminary simulator observations; they are not a publication-level finding.

## Motivation and central question

Wi-Fi 6 (IEEE 802.11ax) and NR-U can operate in unlicensed spectrum. Their transmissions may contend for or interfere in the same band, while their channel-access and medium-sharing behavior differ. This project asks:

**How does end-to-end latency, including its tail, change under increasing offered load when Wi-Fi 6 and NR-U coexist using different channel-access mechanisms?**

The intended dependent outcomes are average latency, P95/P99/P99.9, throughput, packet loss, fairness, and channel-access behavior. The human researcher owns scientific hypotheses and interpretation; future experiments must not silently change the question or assumptions.

## Current simulation

The installed official `cttc-nr-wifi-interference` example creates an NR gNB/UE link and a Wi-Fi AP/STA link in a shared 5.2 GHz, 20 MHz spectrum channel with indoor-office propagation. A remote host sends UDP traffic toward both access links. The baseline selects Wi-Fi 802.11ax at 5 GHz and NR gNB Cat 4 LBT. Mission 2 adds source-application TX and sink-application RX traces to produce one record per transmitted packet without replacing the example's SQLite statistics.

The diagrams and implementation details are in [simulator architecture](docs/architecture/simulator.md), [coexistence implementation](docs/architecture/coexistence.md), and [packet/measurement flow](docs/architecture/packet-flow.md).

Mission 3 stopped application sources at 4.0 s and let sinks run to 4.9 s to observe a drain interval. It used 3.5 s active traffic, loads of 0.5/2/12 Mbps per enabled technology, and 10/5/3 independent seeds respectively. Matched 2 Mbps Wi-Fi-only and NR-only references used three seeds each. All 49,838 transmitted packets in the primary mixed/reference set had unique receptions before simulation stop; this is not evidence of zero underlying drops outside the observed window. The complete design, sample counts, measured outcomes, and uncertainty are in the [Mission 3 report](docs/missions/mission-3-latency-under-load-pilot.md).

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
- [Mission 3 — Controlled latency-under-load pilot](docs/missions/mission-3-latency-under-load-pilot.md): calibration, replicated fixed-mechanism pilot, references, analysis, evidence, and limits.

The [mission history index](docs/MISSIONS.md) is chronological. [Decision records](docs/decisions/README.md) capture engineering and research choices.

## Known limitations

- Upstream describes NR-U/Wi-Fi coexistence as experimental; this simulator model is not proof of standards conformance or real-world deployment performance.
- The baseline is one short run with 62 packets per technology; tail quantiles at this size are unstable and are not generalizable.
- The Mission 3 pilot uses a 4.9 s simulator horizon because this build asserts on a negative NR UE variable-TTI scheduling delay at 5.018928564 s in a longer run. It has not been shown to reach steady state, and the selected highest load reached only about 20% measured occupancy, not demonstrated saturation.
- Mission 3's P99.9 values are exploratory; the reporting gate is 10,000 pooled received samples, which still gives only about 16 observations in the top 0.1%. The 12 Mbps NR run means were numerically identical across three seeds for an unverified reason.
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

## Project transition

This archive remains available at [kirolossedra/nru-publication](https://github.com/kirolossedra/nru-publication). Active work on 5G RAN performance and resource allocation is maintained separately at [kirolossedra/oran-publication](https://github.com/kirolossedra/oran-publication). The O-RAN project selects ns-3.48, 5G-LENA v5.1, ns3-ai, and Orange ib-ORAN; see its compatibility document for evidence and installation status. The legacy ns-3.35/NR v1.2/NR-U source tree is not carried into that environment.
