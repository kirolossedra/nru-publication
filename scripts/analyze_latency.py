#!/usr/bin/env python3
"""Summarize per-packet application-boundary latency CSV and plot distributions."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("results/latency-analysis"))
    parser.add_argument("--deadlines-us", default="100,500,1000",
                        help="comma-separated application E2E deadlines in microseconds")
    args = parser.parse_args()
    deadlines = [float(x) for x in args.deadlines_us.split(",") if x.strip()]
    if not deadlines or any(x < 0 for x in deadlines):
        parser.error("deadlines must contain nonnegative microsecond values")

    by_tech = defaultdict(list)
    tx_ids = set()
    with args.input.open(newline="") as source:
        for row in csv.DictReader(source):
            key = (row["technology"], row["flow_id"], int(row["packet_id"]))
            if key in tx_ids:
                raise ValueError(f"duplicate packet record: {key}")
            tx_ids.add(key)
            rx = row["rx_timestamp_ns"]
            delivered = row["status"] == "received"
            if delivered != bool(rx):
                raise ValueError(f"inconsistent receive status for {key}")
            if delivered:
                latency = int(row["latency_ns"]) / 1000.0
                if latency < 0:
                    raise ValueError(f"negative latency for {key}")
                by_tech[row["technology"]].append(
                    (row["flow_id"], int(row["tx_timestamp_ns"]), latency))
            else:
                by_tech[row["technology"]]  # retain technology with zero delivered samples

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.out_dir / "latency-summary.csv"
    columns = ["technology", "tx_packets", "received_packets", "not_received_by_stop",
               "packet_loss_ratio", "mean_us", "median_us", "p95_us", "p99_us",
               "p99_9_us", "mean_abs_jitter_us"] + [f"deadline_violation_ratio_{d:g}us" for d in deadlines]
    with summary_path.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=columns)
        writer.writeheader()
        all_delivered = []
        for technology in sorted({key[0] for key in tx_ids}):
            items = sorted(by_tech[technology], key=lambda x: (x[0], x[1]))
            values = np.asarray([item[2] for item in items], dtype=float)
            tx_n = sum(1 for key in tx_ids if key[0] == technology)
            rx_n = len(values)
            lost = tx_n - rx_n
            if lost < 0:
                raise ValueError(f"more receives than transmissions for {technology}")
            jitter = []
            previous = {}
            for flow, _, latency in items:
                if flow in previous:
                    jitter.append(abs(latency - previous[flow]))
                previous[flow] = latency
            row = {"technology": technology, "tx_packets": tx_n,
                   "received_packets": rx_n, "not_received_by_stop": lost,
                   "packet_loss_ratio": lost / tx_n if tx_n else ""}
            if rx_n:
                row.update(mean_us=float(np.mean(values)), median_us=float(np.median(values)),
                           p95_us=float(np.percentile(values, 95)),
                           p99_us=float(np.percentile(values, 99)),
                           p99_9_us=float(np.percentile(values, 99.9)),
                           mean_abs_jitter_us=float(np.mean(jitter)) if jitter else 0.0)
                all_delivered.extend((technology, value) for value in values)
            else:
                row.update({name: "" for name in ["mean_us", "median_us", "p95_us", "p99_us", "p99_9_us", "mean_abs_jitter_us"]})
            # Not received by stop is conservatively counted as a deadline violation.
            for deadline in deadlines:
                misses = lost + sum(1 for value in values if value > deadline)
                row[f"deadline_violation_ratio_{deadline:g}us"] = misses / tx_n if tx_n else ""
            writer.writerow(row)

    for technology in sorted(by_tech):
        values = [item[2] for item in by_tech[technology]]
        if values:
            plt.hist(values, bins="auto", alpha=0.65, label=f"{technology} (n={len(values)})")
    plt.xlabel("Application end-to-end latency (µs)")
    plt.ylabel("Packet count")
    plt.title("Latency distribution by access technology")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.out_dir / "latency-distribution.png", dpi=160)
    plt.close()

    for technology in sorted(by_tech):
        values = np.sort([item[2] for item in by_tech[technology]])
        if len(values):
            ecdf = np.arange(1, len(values) + 1) / len(values)
            plt.step(values, ecdf, where="post", label=f"{technology} (n={len(values)})")
    plt.xlabel("Application end-to-end latency (µs)")
    plt.ylabel("Empirical cumulative probability")
    plt.title("Empirical CDF of received-packet latency")
    plt.ylim(0, 1.01)
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(args.out_dir / "latency-ecdf.png", dpi=160)
    plt.close()
    print(summary_path)
    print(args.out_dir / "latency-distribution.png")
    print(args.out_dir / "latency-ecdf.png")


if __name__ == "__main__":
    main()
