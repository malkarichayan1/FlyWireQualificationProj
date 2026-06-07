"""
Phase 1: Load each edge list as a directed graph, de-duplicate edges,
remove self-loops (reporting counts), and print a per-dataset summary.

Edge convention (verified by inspecting headers): column 1 = source
(pre-synaptic), column 2 = target (post-synaptic). Weights are absent in
these files; all graphs are treated as unweighted directed graphs.

Outputs cleaned edge lists as Parquet to data/clean/ for fast reuse, plus a
summary table to output/dataset_summary.csv.
"""
import os
import numpy as np
import pandas as pd

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
CLEAN = os.path.join(DATA, "clean")
os.makedirs(CLEAN, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

DATASETS = ["banc", "fafb", "manc", "maol", "mcns"]


def load_clean(name):
    """Read data/<name>.csv and clean it. Renames the two columns to
    source/target (locking in the convention col1 = pre-synaptic, col2 =
    post-synaptic), removes self-loops, and de-duplicates directed edges.
    Returns (cleaned DataFrame, dict of counts removed)."""
    path = os.path.join(DATA, f"{name}.csv")
    df = pd.read_csv(path, dtype={"source neuron id": "int64", "target neuron id": "int64"})
    df.columns = ["source", "target"]
    n_raw = len(df)

    # self-loops
    self_mask = df["source"] == df["target"]
    n_self = int(self_mask.sum())
    df = df[~self_mask]

    # de-duplicate directed edges
    n_before_dedup = len(df)
    df = df.drop_duplicates(subset=["source", "target"]).reset_index(drop=True)
    n_dups = n_before_dedup - len(df)

    return df, dict(raw_rows=n_raw, self_loops=n_self, dup_edges=n_dups)


def summarize(name, df):
    """Compute per-dataset reporting stats: node/edge counts, density, and
    mean/median/max in- and out-degree. Pure reporting, no side effects."""
    nodes = pd.unique(pd.concat([df["source"], df["target"]], ignore_index=True))
    n_nodes = len(nodes)
    n_edges = len(df)
    outdeg = df.groupby("source").size()
    indeg = df.groupby("target").size()
    return {
        "dataset": name,
        "nodes": n_nodes,
        "edges": n_edges,
        "density": n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0.0,
        "mean_outdeg": n_edges / n_nodes,
        "max_outdeg": int(outdeg.max()),
        "max_indeg": int(indeg.max()),
        "median_outdeg": float(outdeg.median()),
        "median_indeg": float(indeg.median()),
    }


def main():
    """Loop the 5 datasets: clean each, cache it as data/clean/<name>.npz (the
    fast format every later script reads), collect stats, and write
    output/dataset_summary.csv."""
    rows = []
    for name in DATASETS:
        df, info = load_clean(name)
        np.savez_compressed(
            os.path.join(CLEAN, f"{name}.npz"),
            source=df["source"].to_numpy(),
            target=df["target"].to_numpy(),
        )
        s = summarize(name, df)
        s.update(info)
        rows.append(s)
        print(f"[{name}] nodes={s['nodes']:,} edges={s['edges']:,} "
              f"self_loops={info['self_loops']:,} dup_edges={info['dup_edges']:,} "
              f"density={s['density']:.2e} max_out={s['max_outdeg']} max_in={s['max_indeg']}")

    summary = pd.DataFrame(rows)[
        ["dataset", "nodes", "edges", "density", "mean_outdeg",
         "median_outdeg", "median_indeg", "max_outdeg", "max_indeg",
         "self_loops", "dup_edges", "raw_rows"]
    ]
    summary.to_csv(os.path.join(OUT, "dataset_summary.csv"), index=False)
    print("\nSaved cleaned parquet files to data/clean/ and summary to output/dataset_summary.csv")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
