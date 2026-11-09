#!/usr/bin/env python3
"""Run isolated Mission 3 coexistence pilot runs without overwriting prior outputs."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/ns-3-dev"
BINARY = SOURCE / "build/contrib/nr-u/examples/ns3.35-cttc-nr-wifi-interference-debug"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["calibration", "pilot", "pilot-revised", "reference"], required=True)
    parser.add_argument("--rates", default="500kbps,2Mbps,8Mbps")
    parser.add_argument("--seeds", default="91", help="comma-separated ns-3 RNG seeds")
    parser.add_argument("--modes", default="mixed", choices=None,
                        help="comma-separated modes: mixed,wifi-only,nr-only")
    parser.add_argument("--active-seconds", type=float, default=3.5)
    parser.add_argument("--drain-seconds", type=float, default=1.0)
    parser.add_argument("--start-seconds", type=float, default=0.5)
    args = parser.parse_args()
    if not BINARY.is_file():
        parser.error(f"built simulator binary not found: {BINARY}")
    rates = [x.strip() for x in args.rates.split(",") if x.strip()]
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    modes = [x.strip() for x in args.modes.split(",") if x.strip()]
    allowed = {"mixed", "wifi-only", "nr-only"}
    if not rates or not seeds or not modes or set(modes) - allowed:
        parser.error("provide rates, seeds, and valid modes")
    if args.active_seconds <= 0 or args.drain_seconds < 0 or args.start_seconds < 0:
        parser.error("active time must be positive; drain/start times must be nonnegative")

    sim_stop = args.start_seconds + args.active_seconds + args.drain_seconds
    traffic_stop = args.start_seconds + args.active_seconds
    env = os.environ.copy()
    lib_path = str(SOURCE / "build/lib")
    env["LD_LIBRARY_PATH"] = lib_path + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    run_root = ROOT / "results/mission3" / args.phase
    run_root.mkdir(parents=True, exist_ok=True)

    for mode in modes:
        enable_nr = mode != "wifi-only"
        enable_wifi = mode != "nr-only"
        for rate in rates:
            rate_tag = re.sub(r"[^A-Za-z0-9_.-]", "_", rate)
            for seed in seeds:
                run_dir = run_root / mode / f"rate-{rate_tag}_seed-{seed}"
                try:
                    run_dir.mkdir(parents=True, exist_ok=False)
                except FileExistsError:
                    raise SystemExit(f"Refusing to overwrite existing run directory: {run_dir}")
                csv_path = run_dir / "per-packet-latency.csv"
                args_list = [
                    str(BINARY), f"--scenario=0", f"--simTime={sim_stop}",
                    f"--trafficStopTime={traffic_stop}", f"--nodeRate={rate}",
                    f"--seed={seed}", "--runId=0", "--wifiStandard=11ax",
                    "--gnbCamType=ns3::NrCat4LbtAccessManager",
                    f"--enableNr={'true' if enable_nr else 'false'}",
                    f"--enableWifi={'true' if enable_wifi else 'false'}",
                    f"--latencyCsv={csv_path}",
                ]
                config = {
                    "phase": args.phase, "mode": mode, "rate_per_enabled_technology": rate,
                    "seed": seed, "run_id": 0,
                    "wifi_standard": "11ax / WIFI_STANDARD_80211ax_5GHZ",
                    "nr_gnb_access_manager": "ns3::NrCat4LbtAccessManager",
                    "enable_nr": enable_nr, "enable_wifi": enable_wifi,
                    "scenario": 0, "start_seconds": args.start_seconds,
                    "traffic_stop_seconds": traffic_stop, "simulation_stop_seconds": sim_stop,
                    "active_traffic_seconds": args.active_seconds, "drain_seconds": args.drain_seconds,
                    "packet_size_bytes": 1000, "frequency_hz": 5.2e9, "bandwidth_hz": 20e6,
                    "ue_distance_m": 5.0, "cell_scan": True, "beam_search_angle_step_deg": 30,
                    "total_tx_power_dbm": 4, "ue_tx_power_dbm": 2,
                    "cat3_cat4_ed_threshold_dbm": -79, "cat2_ed_threshold_dbm": -69,
                    "propagation": "3GPP indoor office mixed, shared spectrum channel",
                    "rlc_model": "RlcUmAlways", "error_model": "ns3::NrEesmIrT1",
                    "sqlite_filename_expected": None,
                    "csv_file": str(csv_path.relative_to(ROOT)),
                    "command": args_list,
                    "working_directory": str(run_dir),
                    "ld_library_path": lib_path,
                }
                (run_dir / "run-config.json").write_text(json.dumps(config, indent=2) + "\n")
                result = subprocess.run(args_list, cwd=run_dir, env=env,
                                        stdout=(run_dir / "execution.log").open("w"),
                                        stderr=subprocess.STDOUT, check=False)
                sqlite_files = sorted(run_dir.glob("*.db"))
                config["exit_code"] = result.returncode
                config["sqlite_files"] = [p.name for p in sqlite_files]
                (run_dir / "run-config.json").write_text(json.dumps(config, indent=2) + "\n")
                print(f"{run_dir.relative_to(ROOT)} exit={result.returncode} db={len(sqlite_files)}")
                if result.returncode != 0:
                    raise SystemExit(f"Run failed; preserve diagnostics at {run_dir}")
                if not csv_path.is_file() or len(sqlite_files) != 1:
                    raise SystemExit(f"Missing CSV or expected one SQLite DB in {run_dir}")


if __name__ == "__main__":
    main()
