# NR-U environment installation and baseline

Updated: 2026-11-08

## Source stack

The project uses the compatible stack specified by the official NR-U README: ns-3.35, 5G-LENA `5g-lena-v1.2.y`, and the NR-U repository's `master` branch. Source repositories live under `source/ns-3-dev`; the NR and NR-U modules are in its `contrib/` directory. Exact repository revisions are recorded in `manifests/commits.txt`.

Official references:
- [NR-U module README and installation instructions](https://gitlab.com/cttc-lena/nr-u/-/blob/master/README.md)
- [NR-U extension documentation](https://cttc-lena.gitlab.io/nr-u/)

## Build and compatibility patch

Host: Ubuntu 24.04.3 LTS, CMake 3.28.3, Python 3.12.3, Git 2.43.0. Configure succeeded with examples/tests enabled and SQLite stats support enabled. The full build completed successfully, including `nr`, `nr-u`, and `wifi`.

The legacy ns-3.35 headers used `uint8_t` without directly including `<cstdint>`. The complete diagnostics showed this in the bit-serializer, bit-deserializer, and Wi-Fi block-ack-type headers. Subsequent member/constructor errors were cascading errors caused by the undeclared type. Three include-only fixes were applied; no protocol logic was changed. The exact patch is `patches/ns-3.35-gcc-fixed-width-includes.patch`.

Build log: `logs/build-resume-1.log`. The successful build took about 5 minutes 9 seconds using `-j 4`. The initial failed attempt remains preserved in `logs/build.log`.

## Verified coexistence baseline

The official `cttc-nr-wifi-interference` example completed with exit code 0. Full output: `logs/baseline.log`. Database: `results/baseline.db` (the generated copy is preserved there; the original output remains in the source tree too).

Default baseline settings, taken from the example source and the command invocation:

- Wi-Fi: `11ax`, explicitly mapped to `WIFI_STANDARD_80211ax_5GHZ` (Wi-Fi 6 / HE, 5 GHz).
- NR gNB channel access: `ns3::NrCat4LbtAccessManager`; UE access is always-on in this example because grant-free uplink is unsupported.
- LBT energy-detection thresholds: Cat 3/4 `-79 dBm`; Cat 2 `-69 dBm` (defaults are set by the example even though this run uses Cat 4).
- Simulation duration: 1.5 s; UDP apps start at 0.5 s.
- Per-node offered rate: 500 kbps.
- Scenario 0; seed 1; run ID 0; default error model `ns3::NrEesmIrT1`; RLC `RlcUmAlways`.
- Invocation: `cd source/ns-3-dev && ./waf --run cttc-nr-wifi-interference`.

Observed database values for this one baseline run (descriptive smoke-run results, not campaign-grade estimates):

| Technology | Throughput (Mbps) | TX bytes | RX bytes | Mean delay (µs) | Mean jitter (µs) | Channel occupancy |
|---|---:|---:|---:|---:|---:|---:|
| NR | 0.509888 | 63,736 | 63,736 | 3,377 | 64 | 0.047141843 |
| Wi-Fi | 0.509888 | 63,736 | 63,736 | 172 | 84 | 0.014472 |

The database has 212 SINR sample rows, 63 channel-request timing rows, and two end-to-end summary rows. MAC failure and simultaneous-transmission tables contain no rows for this baseline; this is not evidence of zero errors/collisions, only that no rows were recorded. Example code has callbacks and output fields for MAC failure and simultaneous-transmission information.

## Capabilities and limits confirmed

- **Confirmed from executed example:** a single co-located NR/Wi-Fi scenario, Wi-Fi 802.11ax at 5 GHz, NR gNB Cat 4 LBT, configurable Cat 2/3/4 gNB manager selection in the example, offered UDP node rate, simulation time, seed/run ID, and per-technology throughput/mean IP delay/jitter/channel-occupancy outputs.
- **Confirmed from module source:** NR-U implements energy detection and category-specific LBT managers. Cat 2 has deterministic defer without random backoff; Cat 3 uses random backoff with fixed contention window; Cat 4 uses random backoff with variable contention window. The example records channel request timing and SINR samples and has MAC failure/simultaneous-TX instrumentation.
- **Not provided by the baseline output:** per-packet end-to-end delay samples or P95/P99/P99.9 latency. The E2E database stores only mean delay/jitter per flow. Tail percentiles require additional per-packet tracing/output code.
- **Not a full experiment campaign:** this is one default-load baseline; it does not sweep load, seeds, or access mechanisms, and it does not calculate fairness. The two technology rows have identical byte counts in this run, but that alone is not a fairness metric.
- **Research limitation:** the NR-U/Wi-Fi coexistence feature is explicitly experimental in upstream documentation. Results need model validation and sensitivity studies before publication claims.

## Reproduction

1. Check out the repositories at the exact revisions in `manifests/commits.txt`.
2. Apply the compatibility patch from the ns-3 repository root: `git apply ../../patches/ns-3.35-gcc-fixed-width-includes.patch`.
3. Configure once with `./waf configure --enable-examples --enable-tests` (SQLite support must be enabled).
4. Build incrementally with `./waf build -j 4`.
5. Run the baseline command above. Example defaults call `RngSeedManager::SetSeed(1)` and `SetRun(0)`.

No clean was performed. The build tree and all existing logs were retained.

## Storage

At initial inspection, 21 GiB was free. After successful build and run, `source/ns-3-dev` occupies about 3.2 GiB, `results` about 32 KiB, and `logs` about 168 KiB; the filesystem has approximately 19 GiB available. See current `df -h .` for the live value.

## Mission 2 update (2026-11-08)

This file records the Mission 1 installation state above. The former limitation that packet-level latency percentiles were unavailable was resolved during Mission 2: the example now exports per-packet application-boundary data and can be analyzed for received-packet quantiles. See [`PER-PACKET-LATENCY.md`](PER-PACKET-LATENCY.md), [`docs/methodology/latency-instrumentation.md`](methodology/latency-instrumentation.md), and [`docs/missions/mission-2-latency.md`](missions/mission-2-latency.md). The baseline DB under `results/baseline.db` remains the preserved Mission 1 DB; the instrumented example writes its current SQLite DB in the source tree and raw latency CSV under `results/`.

Latest observed storage: `source/ns-3-dev` about 3.2 GiB, `results` about 144 KiB, `logs` about 180 KiB, `patches` about 8 KiB, and approximately 19 GiB available. These values reflect the Mission 2 artifacts and can change; use `df -h .` and `du -sh` for current readings.

The instrumented Mission 2 SQLite database is additionally preserved as `results/mission2-instrumented.db`; `results/mission2-sqlite-comparison.txt` contains the exact Mission 1/Mission 2 E2E query comparison.
