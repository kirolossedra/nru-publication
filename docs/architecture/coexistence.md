# NR-U and Wi-Fi coexistence in the installed example

## Concepts

**NR-U** is New Radio operation in unlicensed spectrum. Unlike licensed NR, unlicensed operation must share spectrum with other users and is modeled here with a channel-access manager that performs listen-before-talk (LBT) before NR transmissions. Wi-Fi devices also perform carrier sensing/contention through their MAC/PHY mechanisms. When both systems use overlapping spectrum, they can defer to energy they sense, transmit at overlapping times when sensing/thresholds differ, and interfere at receivers. Actual outcomes depend on model configuration and propagation.

This project uses the CTTC NR-U extension on top of 5G-LENA NR. Upstream labels Wi-Fi coexistence experimental; this environment verifies that the example executes and exposes these mechanisms, not that every behavior is standards-compliant.

## Implemented access mechanisms

The source comments in `nr-lbt-access-manager.h` describe the categories:

- **Category 2:** deterministic defer without random backoff.
- **Category 3:** random backoff with fixed contention window.
- **Category 4:** random backoff with variable contention window.
- **Category 1:** switching gap; not implemented as an independent CAM subtype in that description.

`cttc-nr-wifi-interference.cc` accepts the gNB manager names `NrCat2LbtAccessManager`, `NrCat3LbtAccessManager`, `NrCat4LbtAccessManager`, `NrOnOffAccessManager`, and `NrAlwaysOnAccessManager`. For the default baseline, it selects `NrCat4LbtAccessManager` at the gNB. The UE access manager is `NrAlwaysOnAccessManager`; the source comment says it should remain always-on because grant-free uplink is not supported in that example. The active traffic direction is downlink from the remote host, so the gNB LBT manager is the channel-access mechanism relevant to this baseline flow.

Wi-Fi 6 is configured through `WifiHelper::SetStandard(WIFI_STANDARD_80211ax_5GHZ)`, an `IdealWifiManager` rate manager, `SpectrumWifiPhy`, and AP/STA MACs. `WifiSetup` traces CCA/PHY state, TXOP/channel-request behavior, and channel occupancy. The access model on the Wi-Fi side is ns-3 Wi-Fi contention, not NR's LBT CAM class.

## Actual coexistence settings

| Setting | Executed default | Evidence |
|---|---|---|
| Frequency/bandwidth | 5.2 GHz / 20 MHz | Example local variables and shared channel setup |
| Wi-Fi | `11ax` maps to 802.11ax at 5 GHz | `wifiStandard` parsing in example |
| NR gNB access | Cat 4 LBT | `gnbCamType` default and NrSingleBwpSetup argument |
| NR UE access | Always-on | `ueCamType` default and source comment |
| ED threshold | Cat 3/4 -79 dBm; Cat 2 -69 dBm | `ConfigureDefaultValues`; Cat 2 value applies when Cat 2 selected |
| Wi-Fi CCA threshold | -62 dBm at AP and STA | `WifiSetup` constructor in example |
| Propagation | 3GPP indoor-office propagation and spectrum models | shared channel setup |

SQLite records channel occupancy, channel-request time, SINR callbacks, MAC data transmission failures and simultaneous transmissions. Empty rows mean no rows were written for that output in that run; they are not automatically proof of zero physical drops or collisions.

## Support versus executed evidence

**Source-supported:** scenario 0 and scenario 1; Wi-Fi `11ac` and `11ax`; NR gNB CAM selection among Cat 2, 3, 4, on/off, and always-on; configurable node rate, simulation time, seed/run, and several PHY/scenario options.

**Executed and verified here:** scenario 0, Wi-Fi 11ax, NR Cat 4 gNB LBT, seed 1/run 0, 500 kbps node rate, 1.5 s total run, 0.5 s app start. Cat 2/Cat 3, 11ac, scenario 1, multiple-load conditions, and other parameters have not been baseline-validated in this project.

**Standards and real-world qualification:** the source's category names and implementation do not independently establish full ETSI/3GPP conformance, certification, regulatory suitability, or hardware equivalence. These require model review and validation beyond a successful run.
