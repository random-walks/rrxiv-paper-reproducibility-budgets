#!/usr/bin/env python3
"""Re-run the per-claim analyses for rrxiv:2605.00003 (Claims 1-3).

This is the entrypoint referenced by the RRP-0019 reproducibility
manifests in this directory (repro/claim-c{1,2,3}.manifest.json). Each
subcommand recomputes one claim's headline statistic from a logged data
table; it does NOT redo the underlying audit or the 17 end-to-end
calibration replications (see each manifest's `notes` for that
asymmetry — it is the paper's own thesis).

Input table schemas
-------------------
Audit table (Claims 1 and 3), CSV with header::

    paper_id,subfield,compute_gpu_hours,wall_time_days,person_hours,materials_usd

  - `subfield` is one of: vision, nlp, tabular.
  - Budget fields are the four-field schema of Claim 4, A100-equivalent
    normalised, one row per audited paper (n=312 in the paper).

Calibration table (Claim 2), CSV with header::

    paper_id,reported_compute_gpu_hours,actual_compute_gpu_hours

  - One row per calibration replication (n=17 in the paper).

Availability: the audit and calibration tables are not yet published as
a standalone dataset (see the paper's open question "Calibration record
as common pool"). This script documents the exact computation so the
analysis is mechanically reproducible the moment the tables are.

Stdlib-only on purpose: runs in a bare python:3.11-slim container.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cmd_c1(audit_table: Path) -> dict[str, object]:
    """Claim 1: share of replications carrying 80% of total compute."""
    rows = _read_rows(audit_table)
    costs = sorted(
        (float(r["compute_gpu_hours"]) for r in rows), reverse=True
    )
    total = sum(costs)
    if total <= 0:
        raise SystemExit("audit table has no positive compute_gpu_hours")
    running, k = 0.0, 0
    for c in costs:
        running += c
        k += 1
        if running >= 0.80 * total:
            break
    return {
        "claim": "rrxiv:2605.00003:claim:c1",
        "n_papers": len(costs),
        "share_of_replications_for_80pct_compute": round(k / len(costs), 4),
        "papers_for_80pct_compute": k,
        "reported_in_paper": 0.08,
    }


def cmd_c2(calibration_table: Path) -> dict[str, object]:
    """Claim 2: median actual/reported compute ratio + IQR."""
    rows = _read_rows(calibration_table)
    ratios = sorted(
        float(r["actual_compute_gpu_hours"])
        / float(r["reported_compute_gpu_hours"])
        for r in rows
    )
    q1, med, q3 = statistics.quantiles(ratios, n=4)
    return {
        "claim": "rrxiv:2605.00003:claim:c2",
        "n_replications": len(ratios),
        "median_actual_over_reported": round(med, 3),
        "iqr": [round(q1, 3), round(q3, 3)],
        "reported_in_paper": {"median": 2.3, "iqr": [1.4, 4.1]},
    }


def _scalar_budget(row: dict[str, str]) -> float:
    """The documented projection from the paper's Approach section:
    b = compute_gpu_hours + 24 * wall_time_days + person_hours,
    then log1p to dampen the tail."""
    b = (
        float(row["compute_gpu_hours"])
        + 24.0 * float(row["wall_time_days"])
        + float(row["person_hours"])
    )
    return math.log1p(b)


def cmd_c3(audit_table: Path) -> dict[str, object]:
    """Claim 3: per-subfield tau + ROC AUC of the scalar budget as a
    discriminator of computationally heavy (vision+nlp) vs tabular."""
    rows = _read_rows(audit_table)
    by_subfield: dict[str, list[float]] = {}
    for r in rows:
        by_subfield.setdefault(r["subfield"], []).append(_scalar_budget(r))
    tau = {s: round(sum(v) / len(v), 4) for s, v in by_subfield.items()}

    heavy = [b for s, v in by_subfield.items() if s in ("vision", "nlp") for b in v]
    light = by_subfield.get("tabular", [])
    if not heavy or not light:
        raise SystemExit("audit table must contain vision/nlp and tabular rows")
    # Mann-Whitney U formulation of ROC AUC (ties count 0.5).
    gt = sum(1 for h in heavy for l in light if h > l)
    eq = sum(1 for h in heavy for l in light if h == l)
    auc = (gt + 0.5 * eq) / (len(heavy) * len(light))
    return {
        "claim": "rrxiv:2605.00003:claim:c3",
        "tau_by_subfield": tau,
        "auc_heavy_vs_tabular": round(auc, 4),
        "reported_in_paper": 0.91,
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("c1", help="80/8 compute-concentration statistic")
    p1.add_argument("--audit-table", type=Path, required=True)
    p2 = sub.add_parser("c2", help="median underreport ratio")
    p2.add_argument("--calibration-table", type=Path, required=True)
    p3 = sub.add_parser("c3", help="reproducibility tax + AUC")
    p3.add_argument("--audit-table", type=Path, required=True)
    args = ap.parse_args(argv)

    if args.cmd == "c1":
        out = cmd_c1(args.audit_table)
    elif args.cmd == "c2":
        out = cmd_c2(args.calibration_table)
    else:
        out = cmd_c3(args.audit_table)
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
