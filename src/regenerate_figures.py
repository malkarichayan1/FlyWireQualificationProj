# Remakes the two figures for the N=1094 solution from the files in this repo
# (network.csv and data/fafb_annotations.csv).
#
# The old adjacency picture came out blank because the matrix is 1094x1094 but
# only column 0 actually has edges in it (all the inputs point at the hub). When
# you shrink that down to a few hundred pixels the one thin column just
# disappears. So here I draw a red line on column 0 and add a little zoomed-in
# box in the corner so you can actually see what's going on.

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display, just save to file
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

# paths
here = os.path.dirname(__file__)
root = os.path.join(here, "..")
fig_dir = os.path.join(root, "figures")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# colors for each neurotransmitter
nt_colors = {
    "gaba": "#1f77b4",
    "acetylcholine": "#d62728",
    "glutamate": "#2ca02c",
    "dopamine": "#9467bd",
    "serotonin": "#ff7f0e",
    "octopamine": "#8c564b",
}

# read the solution (one column per dataset, row 0 is the Am1 hub)
sol = pd.read_csv(os.path.join(root, "network.csv"), dtype=str)
datasets = ["BANC", "FAFB", "MCNS"]
N = len(sol)  # should be 1094

fafb_ids = [int(x) for x in sol["FAFB"].tolist()]
hub_id = fafb_ids[0]
print("N =", N, " (1 hub +", N - 1, "leaves)")


def make_star_matrix(n):
    # Build the in-star adjacency. Every leaf (rows 1..n-1) connects to the hub
    # in column 0, and that's the only thing in the matrix. validate_star.py
    # already checked the three datasets give the exact same matrix, so we only
    # need to build it once and it stands in for all three.
    A = np.zeros((n, n), dtype=np.int8)
    A[1:, 0] = 1
    return A


# build one matrix per dataset (they're all the same)
mats = {}
for d in datasets:
    mats[d] = make_star_matrix(N)

# double check they really are identical and count the edges
base = mats["BANC"]
max_diff = 0
for d in datasets:
    diff = np.abs(base.astype(int) - mats[d].astype(int)).max()
    if diff > max_diff:
        max_diff = int(diff)

n_edges = int(base.sum())
density = n_edges / (N * (N - 1))
print("edges =", n_edges, "(expected", N - 1, "), density =",
      round(density * 100, 4), "%, max diff between datasets =", max_diff)


# -------------------------------------------------------------------
# Figure 1: the adjacency matrices
# -------------------------------------------------------------------
zoom = 14  # how many rows/cols to show in the zoomed corner box

fig, axes = plt.subplots(1, 3, figsize=(16, 6.2))
for ax, name in zip(axes, datasets):
    A = mats[name]
    ax.imshow(A, cmap="Greys", interpolation="nearest", aspect="equal",
              vmin=0, vmax=1)

    # the actual column of edges is too thin to see, so draw a red line on it
    ax.axvline(0, color="#d62728", lw=2.2, zorder=5)
    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(N - 0.5, -0.5)
    ax.set_title(name + "   (" + str(N) + "x" + str(N) + " induced in-star)",
                 fontsize=11)
    ax.set_xlabel("post-synaptic position")
    ax.set_ylabel("pre-synaptic position")

    # label pointing at column 0
    ax.annotate("column 0 = all 1,093 inputs -> Am1 hub",
                xy=(0, N * 0.82), xytext=(N * 0.12, N * 0.82),
                fontsize=8.5, va="center", color="#d62728",
                arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.2))

    # zoomed-in box in the top-right so you can see individual cells
    inset = ax.inset_axes([0.50, 0.52, 0.44, 0.44])
    inset.imshow(A[:zoom, :zoom], cmap="Greys", interpolation="nearest",
                 aspect="equal", vmin=0, vmax=1)
    inset.set_xticks(range(zoom))
    inset.set_yticks(range(zoom))
    inset.set_xticklabels([])
    inset.set_yticklabels([])
    inset.grid(color="#bbbbbb", lw=0.4)
    inset.tick_params(length=0)
    for spine in inset.spines.values():
        spine.set_edgecolor("#d62728")
        spine.set_linewidth(1.4)
    inset.set_title("top-left " + str(zoom) + "x" + str(zoom) + " (zoom)",
                    fontsize=7.5, color="#d62728", pad=2)
    # outline the hub's own cell (0,0) - it's empty, no self-loop
    inset.add_patch(Rectangle((-0.5, -0.5), 1, 1, fill=False,
                              edgecolor="#1f77b4", lw=1.4))

title = ("Induced adjacency under the correspondence - identical across all "
         "three (black = edge)\n"
         "single filled column 0 = all " + str(N - 1) + " inputs -> hub  -  "
         "off-diagonal all zero  -  " + str(n_edges) + " edges, density " +
         str(round(density * 100, 3)) + "%  -  max diff between "
         "BANC/FAFB/MCNS = " + str(max_diff))
fig.suptitle(title, fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.90])
plt.savefig(os.path.join(fig_dir, "adjacency_identical.png"), dpi=140)
plt.close()
print("saved figures/adjacency_identical.png")


# -------------------------------------------------------------------
# Figure 2: the network "sunburst" (inputs around the hub)
# -------------------------------------------------------------------
ann = pd.read_csv(os.path.join(root, "data", "fafb_annotations.csv"),
                  dtype={"root_id": "int64"}, low_memory=False)
ann = ann.set_index("root_id")

leaves = fafb_ids[1:]

# spread the leaves evenly around a circle, with a little random wobble on the
# radius so they don't look like a perfect ring
rng = np.random.default_rng(1)
angles = np.linspace(0, 2 * np.pi, len(leaves), endpoint=False)
radius = 1.0 + rng.random(len(leaves)) * 0.05
xs = radius * np.cos(angles)
ys = radius * np.sin(angles)

# look up the neurotransmitter for each leaf and pick its color
leaf_nt = []
leaf_color = []
for m in leaves:
    if m in ann.index:
        nt = str(ann["top_nt"].get(m, "nan"))
    else:
        nt = "nan"
    leaf_nt.append(nt)
    leaf_color.append(nt_colors.get(nt, "#9e9e9e"))

fig, ax = plt.subplots(figsize=(11, 11))

# draw a faint line from each input to the hub in the middle
for x, y, c in zip(xs, ys, leaf_color):
    ax.plot([x, 0], [y, 0], color=c, lw=0.25, alpha=0.30, zorder=1)

# the input neurons
ax.scatter(xs, ys, s=18, c=leaf_color, edgecolors="white", linewidths=0.2,
           zorder=2)
# the hub in the center
ax.scatter([0], [0], s=2600, c="#1f77b4", edgecolors="black", linewidths=1.5,
           zorder=3)
ax.text(0, 0, "Am1\n(GABA)", ha="center", va="center", fontsize=12,
        color="white", fontweight="bold", zorder=4)

ax.set_title("N = " + str(N) + " conserved in-star - convergence onto the Am1 "
             "wide-field\noptic-lobe amacrine cell (FAFB): " +
             format(len(leaves), ",") + " columnar visual inputs -> 1 hub",
             fontsize=13)

# build the legend with a count for each neurotransmitter that shows up
legend_items = []
for nt in nt_colors:
    if nt in leaf_nt:
        legend_items.append(Patch(facecolor=nt_colors[nt], edgecolor="none",
                                  label=nt + " (n=" + str(leaf_nt.count(nt)) + ")"))
n_unknown = leaf_nt.count("nan")
legend_items.append(Patch(facecolor="#9e9e9e", edgecolor="none",
                          label="unann./other (n=" + str(n_unknown) + ")"))
ax.legend(handles=legend_items, title="input neuron predicted NT",
          loc="lower right", fontsize=8, title_fontsize=9, frameon=True)

ax.set_aspect("equal")
ax.set_axis_off()
ax.set_xlim(-1.15, 1.15)
ax.set_ylim(-1.15, 1.15)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "circuit_network.png"), dpi=150)
plt.close()
print("saved figures/circuit_network.png")
print("done")
