# Largest Shared Circuit Across Three Fly Brains

**My answer: N = 1094**

## Aim of project

Finding the largest group of neurons that appears in three different fly brain connectomes where the wiring pattern is the same. My answer is 1094 neurons which are across the BANC, FAFB, and MCNS datasets. The shared wiring pattern was a directed in-star with 1,093 neurons all feeding into a single central hub neuron. That hub is of the same cell type across the datasets and is Am1, a neuron of the optic lobe.

## Repository layout Path

1. **Network.csv**: There are 3 columns which represent BANC, FAFB, MCNS and 1094 rows. Row 0 is the Am1 hub and the rows from 1 to 1093 are its respective inputs or leaves. Each row is one matched neuron position across all three datasets.
2. **Science.md**: This is a one page scientific summary with figures, biological interpretation, and citations.
3. **Figures/circuit_network.png**: The in-star (sunburst-like) 1,093 input neurons pointing at Am1, colored by neurotransmitter type represent the structure of the network.
4. **Figures/adjacency_identical.png**: The 1094-by-1094 induced adjacency matrix is shown side-by-side for all three datasets to confirm they are identical in shape.
5. **Data/fafb_annotations.csv**: The 1094 FAFB neurons joined to their cell type, neurotransmitter, and side annotations from the FlyWire-783 reference table.
6. **Data/fafb_root_ids.txt**: FAFB root IDs are listed (with hubs first) to load data into Codex or a 3D viewer for a more realistic representation.
7. **Data/codex_query.txt**: A ready-to-paste filter query to pull up all 1094 neurons in Codex website.
8. **Data/neuroglancer_link.txt**: A direct link to view all 1094 neuron meshes in the FlyWire-783 3D viewer. src

## How it works

The five connectome datasets share no neuron IDs; they aren't from the same fly. Finding a matching circuit across them is NP-hard and completely intractable at connectome scale due to there being a huge amount (100,000+) neurons and edge combination. Our solution sidesteps this brutal process. Instead of searching for a matching circuit, we target a motif where all the nodes are interchangeable: a clean directed star. In a clean in-star, every leaf neuron is essentially equivalent to every other in the star. Thus, any two clean in-stars of the same size (N) are automatically isomorphic, so no node-by-node alignment search is needed.

**Additionally info:** A clean in-star of size N has one hub and N-1 leaves, where:

- every leaf sends a connection to the hub
- the hub sends no connection back to any leaf
- no leaf connects to any other leaf so the leaves form an independent set
- The resulting induced adjacency matrix is exactly one filled column and zeros everywhere else. So it proves that all the leaves only connect back to the hub.

## Process

1. Clean and load each dataset's edge list as a directed graph (weights do not matter), remove self-loops, and remove duplicate edges.
2. For each dataset, look at the highest in-degree hub candidates and collect their "pure" presynaptic partners. This is because these are the neurons that connect to the hub but receive no connection back.
3. Then find the largest independent set among those partners. Since this is NP hard, we use a randomized greedy approach which repeatedly picks the lowest-degree remaining neuron, removes its neighbors from consideration, and keeps the best result across multiple random restarts.
4. The matched N for the trio is the minimum star size across all three datasets. In this example, BANC's Am1 hub, with 1,723 clean inputs, is the binding constraint. So N is maximized at 1094.
5. Validate: Order the neurons hub-first, rebuild the NxN adjacency matrix from the original raw edge lists for each dataset independently
6. Confirm the four following conditions:
   1. All three matrices are element-wise identical
   2. The matrix has only 1 column filled so it is a star.
   3. The leaves form an independent set with no reverse edges to the hub
   4. The graph is weakly connected. Only if all four checks pass is the solution written to disk.
7. Outputs: Generate the figures, annotation table, root ID list, Codex query, and Neuroglancer viewer link.

## Assumptions

- Connections are either present or not. The strength of the connection (essentially how many synapses) is ignored. Direction matters between connections. Only connections between the chosen neurons count, so connections to neurons outside the group are ignored.
- Neurons don't need to be the same neuron across datasets. The match is based purely on wiring pattern, not identity. There's no assumption that a neuron in BANC is the same cell as another neuron in FAFB. For a star this doesn't matter anyway since every leaf plays the same role. Therefore, any leaf can pair with any other leaf.
- The circuit must be connected. A group of neurons with no connections between them would satisfy the project requirements, but it's biologically useless.
- The search finds a very good answer, but it's not guaranteed that it's the perfect answer. The step that finds the largest group of unconnected leaves uses a specific strategy rather than checking every possibility. So N = 1094 is a solid result but might not be the absolute maximum theoretically possible. However, we do know that it's a valid possibility because it's been verified to be real across the 3 datasets.
- The best three datasets are BANC, FAFB, and MCNS. This is because the search was run across all five datasets and MANC and MAOL didn't produce the largest result.
- Biology labels are only significant after creating the set. Cell type, neurotransmitter, and side information play no role in finding the circuit and are obtained using public tables of knowledge.

## Instructions to reproduce results

**NOTE:** Before running anything, make sure you have Python 3 installed with the following packages: numpy, pandas, python-igraph, and matplotlib.

1. Download all five edge list CSV files into the `../data/` folder from:
   https://storage.googleapis.com/flywire-data/internship_projects/edge_lists/
2. Clean the data and compute dataset summaries. Run: `python src/load_and_summarize.py`
3. Search for the largest star in each dataset. Run: `python src/star_search.py`
4. Validate the match and write the solution CSV. Run: `python src/validate_star.py solution.csv in banc fafb mcns`
5. Generate all figures and 3D viewer assets. Run: `python src/make_1094_deliverables.py`

To regenerate the figures only. Run: `python src/regenerate_figures.py`

- Use this shortcut if you only want to check the visual outputs and don't want to download and process the full edge list files. This works entirely from files already saved in the repository.
