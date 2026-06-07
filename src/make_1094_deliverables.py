"""
Build the full deliverable set for the N=1094 solution (BANC/FAFB/MCNS in-star,
hub = Am1 wide-field optic-lobe amacrine cell) into the FLYWIRE2/ folder.

Outputs (FLYWIRE2/):
  solution.csv                  the 1094-row, 3-column correspondence
  fafb_1094_annotations.csv     FAFB members joined to 783 annotations
  circuit_network_1094.png      in-star "sunburst": 1093 inputs -> Am1 hub
  adjacency_identical_1094.png   the 1094x1094 matrices, identical across 3
  fafb_root_ids_1094.txt        FAFB root IDs (hub first) for Codex/3D
  codex_query_1094.txt          root_id == .. || .. query for Codex
  neuroglancer_link_1094.txt    3D viewer link (FlyWire 783 meshes)
"""
import os, json, urllib.parse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "output")
CLEAN = os.path.join(ROOT, "data", "clean")
DEST = os.path.join(ROOT, "FLYWIRE2")
os.makedirs(DEST, exist_ok=True)
TRIO = ["banc", "fafb", "mcns"]
NT_COLORS = {"gaba": "#1f77b4", "acetylcholine": "#d62728", "glutamate": "#2ca02c",
             "dopamine": "#9467bd", "serotonin": "#ff7f0e", "octopamine": "#8c564b"}


def adjacency(name, ordered):
    d = np.load(os.path.join(CLEAN, f"{name}.npz"))
    s, t = d["source"], d["target"]
    ns = np.array(sorted(int(x) for x in ordered))
    mask = np.isin(s, ns) & np.isin(t, ns)
    idx = {nid: i for i, nid in enumerate(ordered)}
    N = len(ordered)
    A = np.zeros((N, N), dtype=np.int8)
    for u, v in zip(s[mask].tolist(), t[mask].tolist()):
        A[idx[u], idx[v]] = 1
    return A


# ---- 1. solution.csv ----
sol = pd.read_csv(os.path.join(OUT, "solution_star_brain_trio.csv"), dtype=str)
sol.to_csv(os.path.join(DEST, "solution.csv"), index=False)
fafb_members = [int(x) for x in sol["FAFB"].tolist()]   # row 0 = Am1 hub
N = len(fafb_members)
print(f"solution.csv copied: {N} rows")

# ---- 2. FAFB annotations ----
ann = pd.read_csv(os.path.join(ROOT, "data", "fafb_annotations.tsv"), sep="\t",
                  dtype={"root_id": "int64"}, low_memory=False)
cols = ["root_id", "super_class", "cell_class", "cell_type", "top_nt",
        "top_nt_conf", "side", "nerve"]
a = ann[ann["root_id"].isin(fafb_members)][cols].copy()
order = {r: i for i, r in enumerate(fafb_members)}
a["pos"] = a["root_id"].map(order)
a = a.sort_values("pos").drop(columns="pos")
a.to_csv(os.path.join(DEST, "fafb_1094_annotations.csv"), index=False)
amap = a.set_index("root_id")
print(f"annotations matched: {len(a)}/{N}")

# ---- 3. network figure: in-star sunburst (inputs -> hub) ----
hub = fafb_members[0]
leaves = fafb_members[1:]
rng = np.random.default_rng(1)
theta = np.linspace(0, 2 * np.pi, len(leaves), endpoint=False)
r = 1.0 + rng.random(len(leaves)) * 0.06
lx, ly = r * np.cos(theta), r * np.sin(theta)
leaf_nt = [str(amap["top_nt"].get(m, "nan")) if m in amap.index else "nan" for m in leaves]
leaf_col = [NT_COLORS.get(nt, "#9e9e9e") for nt in leaf_nt]

fig, ax = plt.subplots(figsize=(11, 11))
# faint edges leaf -> hub (convergence)
for x, y, c in zip(lx, ly, leaf_col):
    ax.plot([x, 0], [y, 0], color=c, lw=0.18, alpha=0.18, zorder=1)
ax.scatter(lx, ly, s=14, c=leaf_col, edgecolors="none", zorder=2)
ax.scatter([0], [0], s=2600, c="#1f77b4", edgecolors="black", linewidths=1.5, zorder=3)
ax.text(0, 0, "Am1\n(GABA)", ha="center", va="center", fontsize=12,
        color="white", fontweight="bold", zorder=4)
ax.set_title("N = 1094 conserved in-star — convergence onto the Am1 wide-field\n"
             "optic-lobe amacrine cell (FAFB): 1,093 columnar visual inputs → 1 hub",
             fontsize=13)
present = [k for k in NT_COLORS if k in set(leaf_nt)]
leg = [Patch(facecolor=NT_COLORS[k], edgecolor="none",
             label=f"{k} (n={leaf_nt.count(k)})") for k in present]
leg.append(Patch(facecolor="#9e9e9e", edgecolor="none",
                 label=f"unann./other (n={leaf_nt.count('nan')})"))
ax.legend(handles=leg, title="input neuron predicted NT", loc="lower right",
          fontsize=8, title_fontsize=9, frameon=True)
ax.set_aspect("equal"); ax.set_axis_off()
plt.tight_layout()
plt.savefig(os.path.join(DEST, "circuit_network_1094.png"), dpi=150)
plt.close()
print("wrote circuit_network_1094.png")

# ---- 4. adjacency figure: rebuild all three, confirm identical ----
mats = {d: adjacency(d, [int(x) for x in sol[d.upper()].tolist()]) for d in TRIO}
A0 = mats["banc"]
identical = all(np.array_equal(A0, mats[d]) for d in TRIO)
print(f"all three 1094x1094 matrices identical (rebuilt from edges): {identical}, "
      f"edges={int(A0.sum())} (expected {N-1})")
fig, axes = plt.subplots(1, 3, figsize=(15, 5.3))
for ax, name in zip(axes, ["BANC", "FAFB", "MCNS"]):
    ax.imshow(mats[name.lower()], cmap="Greys", interpolation="nearest", aspect="auto")
    ax.set_title(f"{name}  (1094×1094 in-star)", fontsize=11)
    ax.set_xlabel("post-synaptic position"); ax.set_ylabel("pre-synaptic position")
fig.suptitle("Induced adjacency under the correspondence — identical across all three "
             "(black = edge; single filled column 0 = all inputs → hub)", fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(os.path.join(DEST, "adjacency_identical_1094.png"), dpi=130)
plt.close()
print("wrote adjacency_identical_1094.png")

# ---- 5. 3D viewer assets (FAFB) ----
with open(os.path.join(DEST, "fafb_root_ids_1094.txt"), "w") as f:
    f.write("\n".join(str(m) for m in fafb_members) + "\n")
q = " || ".join(f"root_id == {m}" for m in fafb_members)
with open(os.path.join(DEST, "codex_query_1094.txt"), "w") as f:
    f.write(q + "\n")
state = {"dimensions": {"x": [1.6e-8, "m"], "y": [1.6e-8, "m"], "z": [4e-8, "m"]},
         "layers": [{"type": "segmentation",
                     "source": "precomputed://gs://flywire_v141_m783",
                     "segments": [str(m) for m in fafb_members],
                     "name": "Am1_in_star_N1094"}],
         "layout": "3d", "showSlices": False}
link = "https://ngl.flywire.ai/#!" + urllib.parse.quote(
    json.dumps(state, separators=(",", ":")), safe="")
with open(os.path.join(DEST, "neuroglancer_link_1094.txt"), "w") as f:
    f.write(link + "\n")
print(f"wrote 3D assets (root ids, codex query, neuroglancer link [{len(link)} chars])")
print("\nDONE -> FLYWIRE2/")
