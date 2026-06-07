"""
Task 2 validation + output. For a given trio and orientation, trim each
dataset's clean star to N = min size, order nodes hub-first, rebuild the N x N
directed adjacency from the ORIGINAL edge lists, and assert:
  (1) all three matrices element-wise identical,
  (2) the matrix is EXACTLY a star (out: only row 0 filled; in: only col 0),
  (3) leaves are an independent set (no leaf-leaf edge) and no reverse hub edge,
  (4) weakly connected.
Writes the trio's solution to the given CSV.

Usage: python validate_star.py <out_csv> <orient> <ds1> <ds2> <ds3>
"""
import os, sys, json
import numpy as np
import pandas as pd

CLEAN = os.path.join(os.path.dirname(__file__), "..", "data", "clean")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")


def load_edge_set(name, nodes):
    """Directed (u,v) edges with both endpoints in `nodes`, read from the
    ORIGINAL cleaned edges (so validation is independent of the search)."""
    d = np.load(os.path.join(CLEAN, f"{name}.npz"))
    src = d["source"]; tgt = d["target"]
    ns = np.array(sorted(nodes))
    mask = np.isin(src, ns) & np.isin(tgt, ns)
    return set(zip(src[mask].tolist(), tgt[mask].tolist()))


def adjacency(name, ordered):
    """N x N directed 0/1 matrix in the given hub-first order."""
    edges = load_edge_set(name, ordered)
    idx = {nid: i for i, nid in enumerate(ordered)}
    N = len(ordered)
    A = np.zeros((N, N), dtype=np.int8)
    for (u, v) in edges:
        A[idx[u], idx[v]] = 1
    return A


def main():
    """Source-of-truth validator for a star. Trim each dataset's star to N=min,
    order hub-first, rebuild matrices from raw edges, and assert: (1) all three
    identical, (2) matrix is EXACTLY a star, (3) leaves independent with no
    reverse hub edge, (4) weakly connected. Only then write the CSV. This is the
    check that correctly rejected the buggy star before the fix."""
    out_csv, orient, d1, d2, d3 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    trio = [d1, d2, d3]
    stars = {d: json.load(open(os.path.join(OUT, f"star_{d}_{orient}.json"))) for d in trio}
    N = min(stars[d]["size"] for d in trio)
    print(f"Trio {trio} orient={orient}: sizes " +
          ", ".join(f"{d}={stars[d]['size']}" for d in trio) + f" -> N={N}")

    ordered = {d: [stars[d]["hub"]] + stars[d]["leaves"][:N - 1] for d in trio}
    mats = {d: adjacency(d, ordered[d]) for d in trio}

    A = mats[trio[0]]
    all_identical = all(np.array_equal(A, mats[d]) for d in trio[1:])

    # expected exact star
    exp = np.zeros((N, N), dtype=np.int8)
    if orient == "out":
        exp[0, 1:] = 1
    else:
        exp[1:, 0] = 1
    is_exact_star = all(np.array_equal(mats[d], exp) for d in trio)

    # explicit independence + reverse-edge checks per dataset
    checks = {}
    for d in trio:
        M = mats[d]
        leaf_block = M[1:, 1:]
        no_leaf_leaf = (leaf_block.sum() == 0)
        if orient == "out":
            hub_edges = M[0, 1:].sum(); reverse = M[1:, 0].sum()
        else:
            hub_edges = M[1:, 0].sum(); reverse = M[0, 1:].sum()
        checks[d] = dict(no_leaf_leaf=bool(no_leaf_leaf),
                         hub_edges=int(hub_edges), reverse=int(reverse))

    und = ((A + A.T) > 0).astype(np.int8)
    seen = {0}; stack = [0]
    while stack:
        u = stack.pop()
        for v in np.nonzero(und[u])[0]:
            if v not in seen:
                seen.add(int(v)); stack.append(int(v))
    weakly_connected = len(seen) == N

    print(f"  all_identical={all_identical}  exact_star={is_exact_star}  "
          f"weakly_connected={weakly_connected}  edges={int(A.sum())}  "
          f"density={A.sum()/(N*(N-1)):.5f}")
    for d in trio:
        print(f"    {d}: leaves_independent={checks[d]['no_leaf_leaf']} "
              f"hub_edges={checks[d]['hub_edges']}(exp {N-1}) reverse_edges={checks[d]['reverse']}(exp 0)")

    assert all_identical and is_exact_star and weakly_connected, "INVALID star"
    for d in trio:
        assert checks[d]["no_leaf_leaf"] and checks[d]["hub_edges"] == N - 1 and checks[d]["reverse"] == 0

    cols = [d.upper() for d in trio]
    sol = pd.DataFrame({c: ordered[d] for c, d in zip(cols, trio)})
    sol.to_csv(os.path.join(OUT, out_csv), index=False)
    print(f"  VALID. Wrote output/{out_csv}  (N={N} rows; row 0 = hub).")


if __name__ == "__main__":
    main()
