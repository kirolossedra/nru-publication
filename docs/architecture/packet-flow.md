# Packet and measurement flow

## Installed downlink flow

The example enables a remote host and Internet stack, assigns IPv4 networks, populates static routes, and populates ARP entries. For each destination UE/STA interface, an `OnOffHelper` creates a UDP source at the remote host and sets a constant offered rate with a 1000-byte packet size and `EnableSeqTsSizeHeader=true`. A matching `PacketSink` is installed on the receiver at UDP port 1234. Applications start at 0.5 s and stop at 1.5 s in the baseline.

The packet traverses the source IP/UDP stack, its selected access device, MAC queue/channel access, PHY and shared spectrum channel, the peer PHY/MAC, then receiver IP/UDP stack and PacketSink. NR downlink scheduling/transmission uses 5G-LENA/NR-U; Wi-Fi downlink uses the AP/STA stack. FlowMonitor observes IP flows. The Mission 2 traces sit at the application boundary, not at the MAC.

### Network topology diagram

```mermaid
flowchart LR
  SRC[Remote host\nOnOff UDP source(s)]
  subgraph SHARED[Shared 5.2 GHz / 20 MHz spectrum channel]
    GNB[NR-U gNB\nCat 4 LBT]
    NUE[NR UE\nNR receive endpoint]
    AP[Wi-Fi 6 AP\n802.11ax / EDCA]
    STA[Wi-Fi 6 STA\n802.11ax receive endpoint]
    PROP[Indoor-office propagation\n3GPP loss and spectrum model]
    GNB <-->|NR radio link| NUE
    AP <-->|Wi-Fi radio link| STA
    GNB -. shared RF environment .- PROP
    AP -. shared RF environment .- PROP
  end
  SRC -->|IP/UDP over NR route| GNB
  SRC -->|IP/UDP over Wi-Fi route| AP
  NUE --> NR_RX[PacketSink / NR flow]
  STA --> WIFI_RX[PacketSink / Wi-Fi flow]
```

The diagram represents the default scenario 0 and the two simultaneous downlink technology flows. The propagation model is shared/configured through the spectrum channel; it is not a standalone radio node. NR gNB and Wi-Fi AP roles are explicit in the helper setup. This topology is the implementation used in the baseline, not a general model of all coexistence deployments.

## Mission 2 trace and identity logic

1. At `OnOffApplication::TxWithSeqTsSize`, the example's `LatencyTx` callback receives the already-created `SeqTsSizeHeader`. `GetTs()` supplies the source application timestamp and `GetSeq()` supplies the application sequence number. The callback creates a ledger row keyed by technology, custom flow ID, and sequence number.
2. The installed source app is classified as NR or Wi-Fi from its destination IPv4 network (NR network 7/8-bit prefix in this scenario is 7; Wi-Fi network prefix is 10), and its stable flow ID is bound to that app trace.
3. Every PacketSink's `RxWithSeqTsSize` trace is bound to its known technology and flow ID from the example's installation order. This explicit binding is used because endpoint addresses in the application traces were not a reliable TX/RX flow key in the initial validation run.
4. `LatencyRx` looks up `(technology, flow_id, sequence)`. Unknown IDs increment `unmatched_receives`; repeated receives increment duplicate counters and do not replace the first receive timestamp.
5. After the simulation, `WriteLatencyCsv` writes each TX ledger row. Received rows contain the RX time and `rx - tx` latency; nonreceived rows retain TX identity with blank RX/latency and `not_received_by_stop`.
6. A validation sidecar records TX count, unique receive count, nonreceipt count, duplicate count, and unmatched receive count. The existing FlowMonitor and SQLite processing still run.

### Packet-flow sequence diagram

```mermaid
sequenceDiagram
  participant O as OnOffApplication (remote host)
  participant IP as IP/UDP + access device
  participant CAM as NR-U LBT / Wi-Fi contention
  participant PHY as Shared channel and peer PHY
  participant S as PacketSink (UE or STA)
  participant L as Latency ledger / SQLite
  O->>L: TxWithSeqTsSize(seq, source timestamp)
  O->>IP: UDP packet with SeqTsSizeHeader
  IP->>CAM: enqueue/request access
  CAM->>PHY: transmit after access opportunity
  PHY->>S: simulated reception and UDP delivery
  S->>L: RxWithSeqTsSize(seq, Simulator::Now())
  L->>L: match technology + flow + seq; reject duplicate sample
  L->>L: write raw CSV row; retain SQLite summary path
```

The CAM participant is conceptual across two distinct technology stacks: NR uses its NR-U access manager; Wi-Fi uses ns-3 Wi-Fi contention. The figure is an event-flow abstraction, not a claim that they share one implementation.

## Files and functions

- `cttc-nr-wifi-interference.cc`: `LatencyTx`, `LatencyRx`, `WriteLatencyCsv`, application trace connection, CSV path option, and post-run validation summary.
- `onoff-application.cc`: emits `TxWithSeqTsSize` before adding the header and sending the UDP packet.
- `packet-sink.cc`: emits `RxWithSeqTsSize` for packets whose sequence/timestamp header is enabled.
- `sqlite-output-manager.cc`: maintains the separate SQL measurements.

Application timestamp = source app packet creation/send callback time. Receive timestamp = packet sink app trace time. This measures application-level end-to-end delay. It does not separately measure the duration between a MAC channel-access request and access grant; that must be instrumented at the MAC/CAM boundary if required.
