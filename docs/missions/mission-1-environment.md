# Mission 1 — Fresh NR-U research environment

**Status:** Complete. Source configuration, build, and baseline evidence are preserved. Later Mission 2 work added packet tracing; this report describes the Mission 1 state and does not supersede current capability documentation.

## Objective and rationale

Establish a self-contained ns-3 environment for genuine NR-U/Wi-Fi coexistence before beginning latency experiments. Compatibility was prioritized over newer releases because the official NR-U extension README named a compatible legacy stack: ns-3.35, 5G-LENA v1.2, and NR-U master. No other ns-3 installation was reused.

## Stack and revisions

Exact source commits: [`manifests/commits.txt`](../../manifests/commits.txt).

- ns-3.35: `ac88b75eac1818c673cf2c939a96ac3005b1f051`
- NR/5G-LENA v1.2 line: `fe0a1d2a5fb7d1547e46042041288a684893ba9e`
- NR-U: `75a45143b1cd382326876a9597e856338673039a`
- Host: Ubuntu 24.04.3 LTS; CMake 3.28.3, Python 3.12.3, Git 2.43.0.

Sources are under `source/ns-3-dev`, with NR and NR-U in `contrib/`. This follows the NR-U project's source README. Configure was run with `./waf configure --enable-examples --enable-tests`; SQLite support was enabled. Build used `./waf build -j 4`.

## Build issue and patch

The first build log (`logs/build.log`) showed undeclared `uint8_t` because ns-3.35 headers omitted `<cstdint>` in `src/network/utils/bit-serializer.h` and `bit-deserializer.h`. Once those were fixed, complete diagnostics in Wi-Fi `block-ack-type.h` showed the same omitted include. Subsequent declaration/member errors were cascading consequences. Three direct includes were added; no behavior or protocol logic was changed. Reproduce with [`ns-3.35-gcc-fixed-width-includes.patch`](../../patches/ns-3.35-gcc-fixed-width-includes.patch).

The incremental successful build is logged at `logs/build-resume-1.log`; it built `nr`, `nr-u`, and `wifi`. A successful full build took about 5m9s at four jobs.

## Baseline and results

The official source example `cttc-nr-wifi-interference` was run with no overrides; `logs/baseline.log` records the run. It completed with exit code 0 and generated `results/baseline.db`. Command:

```sh
cd source/ns-3-dev
./waf --run cttc-nr-wifi-interference
```

Effective defaults include scenario 0, NR+Wi-Fi enabled, Wi-Fi 11ax/802.11ax 5 GHz, NR gNB Cat 4 LBT, UE always-on access, 5.2 GHz/20 MHz shared channel, `nodeRate=500kbps`, `simTime=1.5s`, app start 0.5s, seed 1, run ID 0, error model `ns3::NrEesmIrT1`, RLC `RlcUmAlways`.

The saved Mission 1 SQLite data reports two E2E flow rows, equal `txBytes=rxBytes=63736` and throughput 0.509888 Mbps for each. Stored mean delays are 3377 µs NR and 172 µs Wi-Fi; mean jitter 64 and 84 µs respectively. Occupancy values are NR 0.047141843 and Wi-Fi 0.014472. Database also has 212 SINR rows and 63 channel-request rows. MAC-failure and simultaneous-TX tables have no rows. These are single-run smoke-test observations, not statistically established results. The original database remains preserved in `results/baseline.db`.

## Capabilities established and limits

The example source explicitly supports Wi-Fi `11ac` and `11ax`; the baseline used 11ax. The gNB manager option exposes Cat 2/3/4 LBT and other access-manager choices. Its SQLite outputs include throughput, aggregate TX/RX bytes, mean E2E delay/jitter, occupancy, channel request timing, SINR, and callback-driven MAC/simultaneous-transmission data. Mission 1 itself did not have per-packet latency CSV; Mission 2 added it.

NR-U/Wi-Fi coexistence is described upstream as experimental. A successful code path does not establish full standards compliance, calibrated propagation, or real-world performance. No load sweep, fairness metric, tail latency, repeated-seed study, or hardware validation was performed.

## Storage and reproduction

At setup start there were about 22 GiB available; after full source/build and Mission 2 outputs about 19 GiB were available. Current size checks should use `du -sh source/ns-3-dev results logs` and `df -h .`. The detailed build status is retained in [`INSTALL-STATUS.md`](../INSTALL-STATUS.md).

## Decisions

See [decision records D-001 through D-003](../decisions/README.md). Some rationale is retrospective inference from the compatibility choice and code diffs; the original selection rationale recorded at the time was to prioritize verified compatibility over newer releases.

Architecture and coexistence details plus the topology and architecture diagrams are maintained in [`docs/architecture/simulator.md`](../architecture/simulator.md) and [`docs/architecture/coexistence.md`](../architecture/coexistence.md).

### Source checkout command pattern

For a new copy of this exact installation (not needed for the current workspace), clone independently and check out the recorded commits before applying the local patch:

```sh
git clone https://gitlab.com/nsnam/ns-3-dev.git source/ns-3-dev
git -C source/ns-3-dev checkout ac88b75eac1818c673cf2c939a96ac3005b1f051
git clone https://gitlab.com/cttc-lena/nr.git source/ns-3-dev/contrib/nr
git -C source/ns-3-dev/contrib/nr checkout fe0a1d2a5fb7d1547e46042041288a684893ba9e
git clone https://gitlab.com/cttc-lena/nr-u.git source/ns-3-dev/contrib/nr-u
git -C source/ns-3-dev/contrib/nr-u checkout 75a45143b1cd382326876a9597e856338673039a
cd source/ns-3-dev
git apply ../../patches/ns-3.35-gcc-fixed-width-includes.patch
./waf configure --enable-examples --enable-tests
./waf build -j 4
```

The exact system package inventory used during Mission 1 was not saved. The NR-U README calls out libc development headers and SQLite development support; the successful configure log is the authoritative record that SQLite support was detected on this host. Install other ns-3 prerequisites according to the upstream installation instructions on a clean host and record exact package versions for future replications.

The copyable procedure above is also automated by [`scripts/install-environment.sh`](../../scripts/install-environment.sh). It refuses to proceed if `source/` exists and writes uniquely named build/configure logs so prior evidence is not overwritten.
