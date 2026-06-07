Largest Shared Circuit Across Three Fly Brain Datasets — N = 1094

Aim of project:
This project solves a challenge: find the largest group of neurons that appears in three different fly brain connectome datasets, where the wiring pattern between those neurons is exactly the same in all three. The goal is to make that group as large as possible.
The answer is 1094 neurons, matched across the BANC, FAFB, and MCNS datasets. The shared wiring pattern turns out to be a directed in-star — 1,093 neurons all feeding into a single central hub neuron. That hub is, independently identified in all three datasets, the same cell type: Am1, a wide-field GABAergic amacrine neuron of the optic lobe.

Repository layout
PathWhat it isnetwork.csvThe solution — 3 columns (BANC, FAFB, MCNS) × 1094 rows. Row 0 is the Am1 hub; rows 1–1093 are its inputs. Each row is one matched neuron position across all three datasets.science.mdOne-page scientific summary with figures, biological interpretation, and citations.figures/circuit_network.pngThe in-star "sunburst" — 1,093 input neurons pointing at Am1, colored by neurotransmitter type.figures/adjacency_identical.pngProof figure: the 1094×1094 induced adjacency matrix, shown side-by-side for all three datasets to confirm they are identical.data/fafb_annotations.csvThe 1094 FAFB neurons joined to their cell type, neurotransmitter, and side annotations from the FlyWire-783 reference table.data/fafb_root_ids.txtFAFB root IDs (hub listed first) for loading into Codex or a 3D viewer.data/codex_query.txtA ready-to-paste filter query to pull up all 1094 neurons in Codex.data/neuroglancer_link.txtA direct link to view all 1094 neuron meshes in the FlyWire-783 3D viewer.src/All source code (see Reproduce section below).
How it works
The core problem. The five connectome datasets share no neuron IDs — they come from different animals and hemispheres. Finding a matching circuit across them is formally equivalent to the maximum common induced subgraph problem, which is NP-hard and completely intractable at connectome scale (100,000+ neurons, millions of edges). This project sidesteps that entirely.
The key insight. Instead of searching for an arbitrary matching circuit, we target a structural motif where all nodes are interchangeable by definition: a clean directed star. In a clean in-star, every leaf neuron is equivalent to every other, so any two clean in-stars of the same size N are automatically isomorphic — no node-by-node alignment search needed. The correspondence is guaranteed by construction.
What "clean in-star" means. A clean in-star of size N has one hub and N?1 leaves, where:
* every leaf sends a connection to the hub,
* the hub sends no connection back to any leaf, and
* no leaf connects to any other leaf (the leaves form an independent set).
The resulting induced adjacency matrix is exactly one filled column (all inputs pointing at the hub) and zeros everywhere else. Two clean in-stars of the same size always produce this identical matrix.

Pipeline (four steps)
Step 1 — Clean (src/load_and_summarize.py)
Load each dataset's edge list as an unweighted directed graph, drop self-loops, and remove duplicate edges.
Step 2 — Search (src/star_search.py)
For each dataset, look at the highest in-degree hub candidates and collect their "pure" presynaptic partners — neurons that connect to the hub but receive no connection back. Then find the largest independent set among those partners (meaning no two of them connect to each other). Finding the maximum independent set is itself NP-hard, so we use a randomized greedy heuristic: repeatedly pick the lowest-degree remaining neuron, remove its neighbors from consideration, and keep the best result across multiple random restarts. The matched N for the trio is the minimum star size across all three datasets — here BANC's Am1 hub, with 1,723 clean inputs, is the binding constraint, giving N = 1094.
Step 3 — Validate (src/validate_star.py)
This is the single source of truth. Order the neurons hub-first, rebuild the N×N adjacency matrix from the original raw edge lists for each dataset independently, and confirm all four of the following:
1. All three matrices are element-wise identical.
2. The matrix is exactly a star (one filled column, zeros elsewhere).
3. The leaves form an independent set with no reverse edges to the hub.
4. The graph is weakly connected.
Only if all four checks pass is the solution written to disk.
Step 4 — Outputs (src/make_1094_deliverables.py)
Generate the figures, annotation table, root ID list, Codex query, and Neuroglancer viewer link.

Assumptions
* Isomorphism is exact. Edges are treated as binary (present or absent); synapse counts and weights are ignored. Direction is preserved, and only edges induced among the N selected neurons are counted.
* Matching is by structure, not identity. No assumption is made that any neuron in one dataset corresponds to a specific neuron in another. The star motif makes that unnecessary — leaves are interchangeable by definition.
* Connectivity is required. The edgeless subgraph would trivially maximize N but is biologically meaningless, so solutions must be weakly connected.
* The search is heuristic, not provably optimal. The independent set step uses a greedy heuristic, so N = 1094 is a strong lower bound — not a guaranteed maximum. The solution itself is fully certified by the matrix-equality test; only its maximality is approximate.
* Three of five datasets. The best trio is BANC, FAFB, and MCNS. The MANC and MAOL datasets were not in the winning group.
* Annotations are external. Cell type, neurotransmitter, and side labels come from public reference tables and are not used during the search — they only help interpret the result afterward.

Reproduce
Requires Python 3 with numpy, pandas, python-igraph, and matplotlib.
# 1. Download the five edge lists into ../data/ from:
#    https://storage.googleapis.com/flywire-data/internship_projects/edge_lists/
# 2. Clean and cache:        python src/load_and_summarize.py
# 3. Search for stars:       python src/star_search.py
# 4. Validate and write CSV: python src/validate_star.py solution.csv in banc fafb mcns
# 5. Figures and 3D assets:  python src/make_1094_deliverables.py
To regenerate just the two figures from files already in this repo (no external edge lists needed):
python src/regenerate_figures.py

Why a star and not something denser?
Two valid solutions satisfy the isomorphism constraint:
* In-star, N = 1094 (this repo): connected, maximizes N, and maps onto a real conserved circuit — convergence onto the Am1 wide-field amacrine cell across three independent datasets.
* Reciprocal clique, N = 38: much denser (every pair of neurons wired in both directions, density = 1.0), corresponding to a recurrent antennal-lobe local-neuron module.
The star wins on raw N; the clique wins on density and biological richness. Both are rigorously validated by the same matrix-equality test. See science.md for the full biological interpretation.

