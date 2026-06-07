# Convergence onto the Am1 Wide-Field Amacrine Cell

## Summary

The shared circuit found across three fruit fly brain datasets (BANC, FAFB, and MCNS) follows a simple pattern: the in-star pattern. Specifically, 1,093 smaller nerve cells all connect into a single central cell (there are no connections between the 1093 cells). The FAFB dataset helps explain the purpose of the central cell and how it relates with other nerve cells to explain biological significance.

## The Hub Cell

The central cell (FAFB ID: 720575940628307026) is called Am1 and is a wide-field amacrine neuron. This means it is a nerve cell in the fly's visual system that spreads across the medulla, lobula, and lobula plate. Its purpose is to release GABA, an inhibitory chemical which signals the other cells to slow down. The cell is deeply connected in the fly visual system, receiving from roughly 2,246 other cells in the FAFB dataset. The same cell is consistent in the other two datasets as well, which confirms it's a real biological structure.

The 1,093 input cells are columnar interneurons, essentially small, narrow nerve cells that each handle microscopically small portions of the fly's vision. About 58% use acetylcholine (an excitatory signal to Am1) and about 42% use glutamate (which can be inhibitory or excitatory depending on context to Am1). In the MCNS dataset, this group of input cells are named types: T4b, T5b, and TmY5a. T4 and T5 are the fly's motion-detecting cells where T4 responds to moving bright edges and T5 to moving dark edges. Additionally, TmY5a controls wide-scale visual processing and helps stabilize the fruit fly's vision. Overarchingly, the Am1 cell is collecting input specifically from the motion-detection part of the visual system.

## Figure 1 — Circuit Diagram

![In-star circuit: 1,093 columnar input cells converging on Am1](figures/circuit_network.png)

The diagram displays the in-star circuit where each other 1093 input cells are colored either red (excitatory / acetylcholine) or green (inhibitory or excitatory / glutamate). Each arrow points doward Am1 in the center and none of the 1093 input cells connect to one another.

## Figure 2 — Structural Proof

![1,094 x 1,094 connectivity matrices, identical across BANC, FAFB, and MCNS](figures/adjacency_identical.png)

The three individual 1,094 x 1,094 connectivity matrices, built from each of the three datasets (across BANC, FAFB, and MCNS), came out identical. It showed a single filled row and column — all 1,093 input cells connecting to Am1, nothing else. This is the exact signature of an in-star structure with no shared edges between the other 1093 inputs.

## Interpretation and Hypothesis

A single wide-field inhibitory cell obtaining signals from roughly 1,000 to 2,600 columnar cells has a purpose for spatial pooling and gain control. Spatial pooling references the process of collecting information from multiple points of the fly's visual field while gain control is a way of adjusting the fly's sensitivity to light levels and motion based on changing conditions.

Because Am1's inputs are filled with T4 and T5 motion-detector cells, the hypothesis is that Am1 collects motion signals across the entire visual field to allow the fly to estimate how much motion it is experiencing visually. Specifically, it computes a field-wide estimate of how much motion and light there is, then uses inhibition to normalize the responses of individual motion channels to ensure that a single channel does not overreact. This would help the fly's visual system stay accurate across varying lighting conditions and contrast levels.

This same structure appears independently in three separate connectome datasets which suggests it is an evolutionarily stable circuit that the fly visual system needs.

*(Note: the conserved biology is the convergence pattern, not the number of neurons.)*

## References

1. Dorkenwald S. et al. (2024) Neuronal wiring diagram of an adult brain. *Nature* 634:124–138. (FlyWire / FAFB)
2. Matsliah A. et al. (2024) Neuronal parts list and wiring diagram for a visual system. *Nature* 634:166–180. (FlyWire optic lobe; amacrine and wide-field cell types)
3. Maisak M.S. et al. (2013) A directional tuning map of Drosophila elementary motion detectors. *Nature* 500:212–216. (T4/T5 motion detectors)
4. Borst A., Haag J., Reiff D.F. (2010) Fly motion vision. *Annual Review of Neuroscience* 33:49–70.
5. Drews M.S. et al. (2020) Dynamic signal compression for robust motion vision in flies. *Neuron* 104:1–17.
