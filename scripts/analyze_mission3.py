#!/usr/bin/env python3
"""Aggregate Mission 3 run directories, validate raw data, and create pilot tables/figures."""
import argparse
import csv
import json
import math
from pathlib import Path
import sqlite3
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "results/mission3"
OUT = RUN_ROOT / "analysis"
DEADLINES_US = (500.0, 1000.0, 5000.0)
T95 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571,
       7: 2.447, 8: 2.365, 9: 2.306, 10: 2.262}


def percentile(values, p):
    return float(np.percentile(np.asarray(values, dtype=float), p)) if values else ""


def sqlite_metrics(db_path):
    with sqlite3.connect(db_path) as db:
        names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        e2e = sorted(x for x in names if x.startswith("e2e_"))
        occupancy = sorted(x for x in names if x.startswith("channel_occupancy_"))
        if len(e2e) != 1 or len(occupancy) != 1:
            raise ValueError(f"unexpected SQLite schema in {db_path}: e2e={e2e}, occupancy={occupancy}")
        e2e_rows = db.execute(f"SELECT TECHNOLOGY,THROUGHPUT_MBPS,TXBYTES,RXBYTES,LATENCY_US,JITTER_US FROM {e2e[0]}").fetchall()
        occ_rows = db.execute(f"SELECT TECHNOLOGY,VALUE FROM {occupancy[0]}").fetchall()
    return ({r[0]: {"achieved_ip_rx_mbps": float(r[1]), "flow_tx_bytes": int(r[2]),
                     "flow_rx_bytes": int(r[3]), "flowmonitor_mean_latency_us": float(r[4]),
                     "flowmonitor_mean_jitter_us": float(r[5])} for r in e2e_rows},
            {r[0]: float(r[1]) for r in occ_rows})


def load_run(config_path):
    run_dir = config_path.parent
    config = json.loads(config_path.read_text())
    csv_path = run_dir / "per-packet-latency.csv"
    dbs = list(run_dir.glob("*.db"))
    if config.get("exit_code") != 0 or not csv_path.is_file() or len(dbs) != 1:
        raise ValueError(f"incomplete or failed run: {run_dir}")
    rows = list(csv.DictReader(csv_path.open(newline="")))
    keys = set()
    by_tech = {}
    for row in rows:
        key = (row["technology"], row["flow_id"], int(row["packet_id"]))
        if key in keys:
            raise ValueError(f"duplicate TX key {key} in {csv_path}")
        keys.add(key)
        tech = row["technology"]
        by_tech.setdefault(tech, {"tx": 0, "rx": [], "lost": 0, "jitter": []})
        cell = by_tech[tech]
        cell["tx"] += 1
        if row["status"] == "received":
            if not row["rx_timestamp_ns"]:
                raise ValueError(f"missing RX time with received status in {csv_path}")
            latency_us = int(row["latency_ns"]) / 1000.0
            if latency_us < 0:
                raise ValueError(f"negative latency in {csv_path}")
            cell["rx"].append((row["flow_id"], int(row["tx_timestamp_ns"]), latency_us))
        elif row["status"] == "not_received_by_stop":
            if row["rx_timestamp_ns"] or row["latency_ns"]:
                raise ValueError(f"nonreceipt has RX measurement in {csv_path}")
            cell["lost"] += 1
        else:
            raise ValueError(f"unknown status {row['status']} in {csv_path}")
    for tech, cell in by_tech.items():
        cell["rx"].sort(key=lambda x: (x[0], x[1]))
        last = {}
        for flow, _, lat in cell["rx"]:
            if flow in last:
                cell["jitter"].append(abs(lat - last[flow]))
            last[flow] = lat

    e2e, occ = sqlite_metrics(dbs[0])
    validation_path = run_dir / "per-packet-latency.csv.validation.txt"
    val = dict(line.strip().split("=", 1) for line in validation_path.read_text().splitlines() if "=" in line)
    expected_tx = sum(c["tx"] for c in by_tech.values())
    expected_rx = sum(len(c["rx"]) for c in by_tech.values())
    expected_lost = sum(c["lost"] for c in by_tech.values())
    if int(val["tx_records"]) != expected_tx or int(val["received_unique"]) != expected_rx:
        raise ValueError(f"validation sidecar disagrees with CSV in {run_dir}")
    if int(val["not_received_by_stop"]) != expected_lost:
        raise ValueError(f"nonreceipt sidecar disagrees with CSV in {run_dir}")

    active = float(config["active_traffic_seconds"])
    pkt = int(config["packet_size_bytes"])
    per_run = []
    for tech, cell in sorted(by_tech.items()):
        tx, rxs = cell["tx"], cell["rx"]
        vals = [r[2] for r in rxs]
        flow = e2e.get(tech, {})
        row = {"phase": config["phase"], "mode": config["mode"],
               "offered_rate_configured": config["rate_per_enabled_technology"],
               "offered_rate_configured_mbps": float(config["rate_per_enabled_technology"].replace("Mbps", "").replace("kbps", "")) * (0.001 if "kbps" in config["rate_per_enabled_technology"] else 1.0),
               "seed": config["seed"], "run_id": config["run_id"], "technology": tech,
               "tx_packets": tx, "rx_packets": len(rxs), "not_received_by_stop": cell["lost"],
               "packet_loss_ratio": cell["lost"] / tx if tx else "",
               "onoff_tx_trace_mbps": tx * pkt * 8.0 / active / 1e6 if active else "",
               "achieved_app_rx_mbps": len(rxs) * pkt * 8.0 / active / 1e6 if active else "",
               "achieved_ip_rx_mbps": flow.get("achieved_ip_rx_mbps", ""),
               "channel_occupancy_ratio": occ.get(tech, ""),
               "mean_latency_us": float(np.mean(vals)) if vals else "",
               "median_latency_us": float(np.median(vals)) if vals else "",
               "p95_latency_us": percentile(vals, 95), "p99_latency_us": percentile(vals, 99),
               "p99_9_latency_us": percentile(vals, 99.9) if len(vals) >= 10000 else "",
               "p99_9_sample_gate": len(vals) >= 10000,
               "mean_abs_jitter_us": float(np.mean(cell["jitter"])) if cell["jitter"] else (0.0 if vals else ""),
               "flowmonitor_tx_bytes": flow.get("flow_tx_bytes", ""),
               "flowmonitor_rx_bytes": flow.get("flow_rx_bytes", ""),
               "flowmonitor_mean_latency_us": flow.get("flowmonitor_mean_latency_us", ""),
               "flowmonitor_mean_jitter_us": flow.get("flowmonitor_mean_jitter_us", ""),
               "run_directory": str(run_dir.relative_to(ROOT)), "sqlite_file": dbs[0].name}
        for deadline in DEADLINES_US:
            row[f"deadline_violation_ratio_{deadline:g}us"] = (
                (cell["lost"] + sum(v > deadline for v in vals)) / tx if tx else "")
        row["_latencies"] = vals
        per_run.append(row)
    return config, per_run


def ci95(values):
    if len(values) < 2:
        return ("", "", "")
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    t = T95.get(len(values), 1.96)
    half = t * sd / math.sqrt(len(values))
    return (sd, mean - half, mean + half)


def main():
    global DEADLINES_US
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=RUN_ROOT)
    parser.add_argument("--out-dir", type=Path, default=OUT)
    parser.add_argument("--deadlines-us", default="500,1000,5000",
                        help="comma-separated application E2E deadlines in microseconds")
    args = parser.parse_args()
    try:
        DEADLINES_US = tuple(float(x) for x in args.deadlines_us.split(",") if x.strip())
    except ValueError:
        parser.error("deadline values must be numeric microseconds")
    if not DEADLINES_US or any(x < 0 or not math.isfinite(x) for x in DEADLINES_US):
        parser.error("deadlines must contain finite, nonnegative microsecond values")
    configs = sorted((args.root / "calibration").glob("**/run-config.json"))
    configs += sorted((args.root / "pilot").glob("**/run-config.json"))
    configs += sorted((args.root / "pilot-revised").glob("**/run-config.json"))
    configs += sorted((args.root / "reference").glob("**/run-config.json"))
    runs = []
    failed_runs = []
    for cfg in configs:
        config = json.loads(cfg.read_text())
        if config.get("exit_code") != 0:
            failed_runs.append({"phase": config.get("phase"), "mode": config.get("mode"),
                                "rate": config.get("rate_per_enabled_technology"), "seed": config.get("seed"),
                                "exit_code": config.get("exit_code"), "run_directory": str(cfg.parent.relative_to(ROOT))})
            continue
        loaded_cfg, rows = load_run(cfg)
        runs.extend(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "failed-runs.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["phase", "mode", "rate", "seed", "exit_code", "run_directory"],
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(failed_runs)
    if not runs:
        raise SystemExit("No completed run configurations found")
    columns = [k for k in runs[0] if k != "_latencies"]
    with (args.out_dir / "seed-run-metrics.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows({k: r.get(k, "") for k in columns} for r in runs)

    groups = {}
    for row in runs:
        key = (row["phase"], row["mode"], row["offered_rate_configured"], row["technology"])
        groups.setdefault(key, []).append(row)
    aggregate_cols = ["phase", "mode", "offered_rate_configured", "technology", "seed_n",
                      "tx_packets_total", "rx_packets_total", "nonreceipt_total", "packet_loss_ratio_mean_seed",
                      "onoff_tx_trace_mbps_mean_seed", "achieved_app_rx_mbps_mean_seed", "achieved_app_rx_mbps_sd_seed",
                      "achieved_app_rx_mbps_ci95_low", "achieved_app_rx_mbps_ci95_high",
                      "achieved_ip_rx_mbps_mean_seed", "achieved_ip_rx_mbps_sd_seed",
                      "achieved_ip_rx_mbps_ci95_low", "achieved_ip_rx_mbps_ci95_high",
                      "channel_occupancy_mean_seed", "channel_occupancy_sd_seed", "channel_occupancy_ci95_low", "channel_occupancy_ci95_high",
                      "mean_latency_mean_seed_us", "mean_latency_sd_seed_us", "mean_latency_ci95_low_us", "mean_latency_ci95_high_us",
                      "median_latency_mean_seed_us", "p95_latency_mean_seed_us", "p99_latency_mean_seed_us",
                      "p99_9_latency_pooled_us", "p99_9_samples_pooled", "mean_abs_jitter_mean_seed_us",
                      *[f"deadline_violation_{d:g}us_mean_seed" for d in DEADLINES_US]]
    aggregate = []
    for key, rows in sorted(groups.items()):
        pooled = [x for row in rows for x in row["_latencies"]]
        def vals(name): return [float(r[name]) for r in rows if r[name] != ""]
        ml = vals("mean_latency_us"); tp = vals("achieved_ip_rx_mbps"); app_tp = vals("achieved_app_rx_mbps"); occ = vals("channel_occupancy_ratio")
        sd, lo, hi = ci95(ml); tpsd, tplo, tphi = ci95(tp); appsd, applo, apphi = ci95(app_tp); osd, olo, ohi = ci95(occ)
        ar = {"phase": key[0], "mode": key[1], "offered_rate_configured": key[2], "technology": key[3],
              "seed_n": len(rows), "tx_packets_total": sum(r["tx_packets"] for r in rows),
              "rx_packets_total": sum(r["rx_packets"] for r in rows), "nonreceipt_total": sum(r["not_received_by_stop"] for r in rows),
              "packet_loss_ratio_mean_seed": statistics.mean(vals("packet_loss_ratio")) if vals("packet_loss_ratio") else "",
              "onoff_tx_trace_mbps_mean_seed": statistics.mean(vals("onoff_tx_trace_mbps")) if vals("onoff_tx_trace_mbps") else "",
              "achieved_app_rx_mbps_mean_seed": statistics.mean(app_tp) if app_tp else "",
              "achieved_app_rx_mbps_sd_seed": appsd,
              "achieved_app_rx_mbps_ci95_low": applo, "achieved_app_rx_mbps_ci95_high": apphi,
              "achieved_ip_rx_mbps_mean_seed": statistics.mean(tp) if tp else "", "achieved_ip_rx_mbps_sd_seed": tpsd,
              "achieved_ip_rx_mbps_ci95_low": tplo, "achieved_ip_rx_mbps_ci95_high": tphi,
              "channel_occupancy_mean_seed": statistics.mean(occ) if occ else "", "channel_occupancy_sd_seed": osd,
              "channel_occupancy_ci95_low": olo, "channel_occupancy_ci95_high": ohi,
              "mean_latency_mean_seed_us": statistics.mean(ml) if ml else "", "mean_latency_sd_seed_us": sd,
              "mean_latency_ci95_low_us": lo, "mean_latency_ci95_high_us": hi,
              "median_latency_mean_seed_us": statistics.mean(vals("median_latency_us")) if vals("median_latency_us") else "",
              "p95_latency_mean_seed_us": statistics.mean(vals("p95_latency_us")) if vals("p95_latency_us") else "",
              "p99_latency_mean_seed_us": statistics.mean(vals("p99_latency_us")) if vals("p99_latency_us") else "",
              "p99_9_latency_pooled_us": percentile(pooled, 99.9) if len(pooled) >= 10000 else "",
              "p99_9_samples_pooled": len(pooled) if len(pooled) >= 10000 else "",
              "mean_abs_jitter_mean_seed_us": statistics.mean(vals("mean_abs_jitter_us")) if vals("mean_abs_jitter_us") else "",
              **{f"deadline_violation_{d:g}us_mean_seed": statistics.mean(vals(f"deadline_violation_ratio_{d:g}us"))
                 if vals(f"deadline_violation_ratio_{d:g}us") else "" for d in DEADLINES_US}}
        aggregate.append(ar)
    with (args.out_dir / "condition-summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=aggregate_cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(aggregate)

    # Figures use the common-horizon replicated pilot only. The preliminary
    # short-horizon pilot and calibration runs are not pooled with it.
    mixed = [r for r in runs if r["phase"] == "pilot-revised" and r["mode"] == "mixed"]
    if mixed:
        rates = sorted({r["offered_rate_configured_mbps"] for r in mixed})
        techs = sorted({r["technology"] for r in mixed})
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for tech in techs:
            for metric, ax, title in [("mean_latency_us", axes[0], "Mean application E2E latency"),
                                      ("p99_latency_us", axes[1], "P99 application E2E latency")]:
                means, sds = [], []
                for rate in rates:
                    group = [float(r[metric]) for r in mixed if r["technology"] == tech and r["offered_rate_configured_mbps"] == rate and r[metric] != ""]
                    means.append(statistics.mean(group) if group else np.nan)
                    sds.append(statistics.stdev(group) if len(group) > 1 else 0)
                    for r in mixed:
                        if r["technology"] == tech and r["offered_rate_configured_mbps"] == rate and r[metric] != "":
                            ax.scatter(rate, float(r[metric]), alpha=0.45, s=18)
                ax.errorbar(rates, means, yerr=sds, marker="o", capsize=3, label=tech)
                ax.set_xscale("log"); ax.set_xlabel("Configured offered rate per technology (Mbps)")
                ax.set_ylabel("Latency (µs)"); ax.set_title(title); ax.grid(True, alpha=0.25)
        axes[0].legend(); axes[1].legend(); fig.tight_layout(); fig.savefig(args.out_dir / "latency-vs-offered-load.png", dpi=160); plt.close(fig)

        fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
        panels = [("achieved_app_rx_mbps", "Received application payload throughput (Mbps)"),
                  ("packet_loss_ratio", "Nonreceipt ratio by simulation stop"),
                  ("channel_occupancy_ratio", "Channel occupancy ratio")]
        for ax, (metric, label) in zip(axes, panels):
            for tech in techs:
                means=[]; sds=[]
                for rate in rates:
                    group=[float(r[metric]) for r in mixed if r["technology"]==tech and r["offered_rate_configured_mbps"]==rate and r[metric]!=""]
                    means.append(statistics.mean(group) if group else np.nan)
                    sds.append(statistics.stdev(group) if len(group)>1 else 0)
                    for r in mixed:
                        if r["technology"]==tech and r["offered_rate_configured_mbps"]==rate and r[metric]!="": ax.scatter(rate,float(r[metric]),alpha=.45,s=18)
                ax.errorbar(rates,means,yerr=sds,marker="o",capsize=3,label=tech)
            if metric == "packet_loss_ratio":
                ax.set_ylim(0, 1)
            ax.set_xscale("log"); ax.set_xlabel("Configured offered rate per technology (Mbps)")
            ax.set_ylabel(label); ax.set_title(label); ax.grid(True,alpha=.25)
        axes[0].legend(); fig.tight_layout(); fig.savefig(args.out_dir / "throughput-loss-occupancy-vs-load.png",dpi=160); plt.close(fig)

        fig, ax = plt.subplots(figsize=(9,6))
        for rate in rates:
            for tech in techs:
                values=sorted(x for r in mixed if r["technology"]==tech and r["offered_rate_configured_mbps"]==rate for x in r["_latencies"])
                if values:
                    ax.step(values,np.arange(1,len(values)+1)/len(values),where="post",label=f"{rate:g} Mbps {tech} n={len(values)}")
        ax.set_xlabel("Application E2E latency (µs)"); ax.set_ylabel("Empirical cumulative probability")
        ax.set_title("Received-packet latency ECDF by offered load")
        ax.set_ylim(0,1.01); ax.grid(True,alpha=.25); ax.legend(fontsize=8); fig.tight_layout()
        fig.savefig(args.out_dir / "latency-ecdf-by-load.png",dpi=160); plt.close(fig)

        fig, ax = plt.subplots(figsize=(9,5))
        seed_colors = {"nr": "tab:blue", "wifi": "tab:orange"}
        for tech in techs:
            for rate in rates:
                group=[float(r["mean_latency_us"]) for r in mixed if r["technology"]==tech and r["offered_rate_configured_mbps"]==rate and r["mean_latency_us"]!=""]
                offsets=np.linspace(-0.025,0.025,len(group)) if len(group)>1 else np.zeros(len(group))
                ax.scatter([rate*(1+o) for o in offsets],group,label=f"{tech} seeds" if rate==rates[0] else None,
                           alpha=.7,s=30,color=seed_colors[tech])
                if group: ax.plot([rate],[statistics.mean(group)],marker="D",color="black",markersize=5,
                                  label="Mean across seeds" if tech==techs[0] and rate==rates[0] else None)
        ax.set_xscale("log"); ax.set_xlabel("Configured offered rate per technology (Mbps)")
        ax.set_ylabel("Per-seed mean application E2E latency (µs)")
        ax.set_title("Seed-level mean latency variation (diamonds show mean)")
        ax.grid(True,alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(args.out_dir / "seed-variation.png",dpi=160); plt.close(fig)

        refs=[r for r in runs if r["phase"]=="reference" and r["mode"] in {"wifi-only", "nr-only"}]
        if refs:
            fig, axes=plt.subplots(1,3,figsize=(15,4.8))
            for ax,metric,label in zip(axes,["mean_latency_us","achieved_app_rx_mbps","channel_occupancy_ratio"],
                                       ["Mean latency (µs)","Received application payload throughput (Mbps)","Channel occupancy"]):
                for mode in sorted({r["mode"] for r in refs+mixed}):
                    for tech in techs:
                        subset=[r for r in refs+mixed if r["mode"]==mode and r["technology"]==tech]
                        if not subset: continue
                        xs=sorted({r["offered_rate_configured_mbps"] for r in subset})
                        ys=[]; es=[]
                        for rate in xs:
                            vs=[float(r[metric]) for r in subset if r["offered_rate_configured_mbps"]==rate and r[metric]!=""]
                            ys.append(statistics.mean(vs) if vs else np.nan)
                            es.append(statistics.stdev(vs) if len(vs)>1 else 0)
                        ax.errorbar(xs,ys,yerr=es,marker="o",capsize=2,label=f"{mode} {tech}")
                ax.set_xscale("log"); ax.set_xlabel("Configured rate per enabled technology (Mbps)")
                ax.set_ylabel(label); ax.set_title(label); ax.grid(True,alpha=.25)
            axes[0].legend(fontsize=7); fig.tight_layout()
            fig.savefig(args.out_dir / "mixed-vs-single-technology.png",dpi=160); plt.close(fig)
    print(f"Analyzed {len(configs)} run directories into {args.out_dir.relative_to(ROOT) if args.out_dir.is_relative_to(ROOT) else args.out_dir}")


if __name__ == "__main__":
    main()
