"""
Task 2: find the largest clean directed STAR in each dataset.

A clean out-star of size N = 1 hub + (N-1) leaves where:
  - hub -> leaf for every leaf            (leaves are out-neighbors of hub)
  - leaf -> hub for NO leaf               (leaves are NOT in-neighbors -> "pure")
  - no leaf -> leaf and no leaf <- leaf   (leaves are an independent set)
The induced adjacency is then exactly one full hub row (minus diagonal), zeros
elsewhere. (in-star = transpose: one full hub column.)

Because leaves are interchangeable, any clean star of size N in each dataset is
isomorphic to any other under the trivial correspondence (hub<->hub). So we find
the biggest clean star *independently* per dataset; the matched N for a trio is
the min over its three datasets (then trim).

We search top out/in-degree hubs and extract a large independent set among the
hub's pure neighbours via randomized greedy (lowest-degree-first + restarts).
Members saved to output/star_<name>_<orient>.json.
"""
import os, json, time
import numpy as np
import igraph as ig

CLEAN = os.path.join(os.path.dirname(__file__), "..", "data", "clean")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
DATASETS = ["banc", "fafb", "mcns", "maol"]
N_HUBS = 60
RESTARTS = 10


def load_graph(name):
    """Shared loader: cleaned .npz -> directed igraph with original IDs in
    g.vs["name"]."""
    d = np.load(os.path.join(CLEAN, f"{name}.npz"))
    src = d["source"].astype(np.int64); tgt = d["target"].astype(np.int64)
    uniq, inv = np.unique(np.concatenate([src, tgt]), return_inverse=True)
    es = inv[:len(src)]; et = inv[len(src):]
    g = ig.Graph(n=len(uniq), edges=list(zip(es.tolist(), et.tolist())), directed=True)
    g.vs["name"] = uniq.tolist()
    return g


def greedy_mis(adj, deg, rng, jitter=0.0):
    """Independent set on undirected adj (list of sets). Lowest-degree-first
    with optional random jitter for restarts. Returns list of chosen indices."""
    n = len(adj)
    key = deg.astype(float)
    if jitter:
        key = key + rng.random(n) * jitter
    order = np.argsort(key)
    removed = np.zeros(n, dtype=bool)
    chosen = []
    for v in order:
        if removed[v]:
            continue
        chosen.append(v)
        removed[v] = True
        for w in adj[v]:
            removed[w] = True
    return chosen


def best_star(g, orient):
    """orient='out' -> out-star; 'in' -> in-star."""
    deg_all = np.array(g.outdegree() if orient == "out" else g.indegree())
    hubs = np.argsort(deg_all)[::-1][:N_HUBS]
    rng = np.random.default_rng(0)
    best = dict(size=0, hub=None, leaves=None)
    for h in hubs:
        if orient == "out":
            nbr = set(g.successors(h)); opp = set(g.predecessors(h))
        else:
            nbr = set(g.predecessors(h)); opp = set(g.successors(h))
        pure = [v for v in nbr if v not in opp]      # no reverse edge to hub
        if 1 + len(pure) <= best["size"]:
            continue
        sub = g.induced_subgraph(pure)  # NOTE: igraph reindexes (sorts) vertices;
        # always map back via sub.vs[...]["name"], never via pure[i].
        u = sub.as_undirected(mode="collapse"); u.simplify()
        adj = [set(u.neighbors(i)) for i in range(u.vcount())]
        deg = np.array(u.degree())
        local_best = []
        for r in range(RESTARTS):
            mis = greedy_mis(adj, deg, rng, jitter=0.0 if r == 0 else float(deg.max() + 1))
            if len(mis) > len(local_best):
                local_best = mis
        size = 1 + len(local_best)
        if size > best["size"]:
            leaves = [int(sub.vs[i]["name"]) for i in local_best]
            best = dict(size=size, hub=int(g.vs[h]["name"]), leaves=leaves,
                        hub_deg=int(deg_all[h]))
    return best


def main():
    """Run both orientations for BANC/FAFB/MCNS/MAOL, save each star's members
    to star_<name>_<orient>.json, and print the matched N (= min) for each
    candidate trio so we can pick the largest valid star."""
    summary = {}
    for name in DATASETS:
        t0 = time.time()
        g = load_graph(name)
        for orient in ("out", "in"):
            b = best_star(g, orient)
            b["dataset"] = name; b["orient"] = orient
            json.dump(b, open(os.path.join(OUT, f"star_{name}_{orient}.json"), "w"))
            summary[(name, orient)] = b["size"]
            print(f"[{name}/{orient}] star_size={b['size']} (hub_deg={b.get('hub_deg')}) "
                  f"{time.time()-t0:.1f}s")
    print("\n=== Best matched N per trio/orientation ===")
    for trio in (["banc", "fafb", "mcns"], ["fafb", "mcns", "maol"]):
        for orient in ("out", "in"):
            N = min(summary[(d, orient)] for d in trio)
            print(f"  {'/'.join(trio):22s} {orient:3s} -> N = {N}")


if __name__ == "__main__":
    main()
