[Português](README.md) · **English**

# Results and visualizations

Figures from the zebrafish pigment cell transcriptomics project. Read the [final paper](../Artigo%20Final.pdf) for methods, context and interpretation.

To generate new outputs in a separate directory, follow the [reproduction workflow](../reproduction/README.md) (instructions in Portuguese). This gallery contains historical images, which are not replaced by those outputs.

The time-specific UMAPs are independent projections: positions and distances across maps do not represent cell trajectories. The modern reproduction checks the calculation, without adding biological conclusions.

For model estimates and cell-abundance variability, the [four-plot and table module](../reproduction/README.md#gráficos-das-estimativas-e-da-abundância-celular) explains reproduction and interpretation (in Portuguese). The new PNG and CSV files are generated in your chosen local folder; they are not part of this historical gallery.

The [reference counts and maps](../reproduction/README.md#contagens-e-mapas-da-referência) have their own workflow (instructions in Portuguese): six PNG and three CSV files are generated locally in `reference-maps/figures-tables`, under the example output location. They draw precomputed coordinates on a common background, unlike UMAPs recalculated separately by time. They do not replace the images below, reproduce the `Oligo` boxplot or establish equivalence with the historical figures.

The [time/Oligo boxplot](../reproduction/README.md#boxplot-por-tempo-e-oligo) now has a separate module, including metadata acquisition (instructions in Portuguese): the usual CSV does not contain `Oligo`. Its two PNG and five CSV files are generated on your computer, in `oligo-run/figures-tables` with the guide's example paths. Start with `boxplot-historical.png` and `filter-summary-by-time.csv`; `excluded-groups.csv` identifies exclusions. The historical `log10(n)` cut between 1.5 and 4.5 removes groups before quartiles are calculated; it is not just a zoom. The second figure provides a comparison without that cut; neither replaces the [historical boxplot in this gallery](fig2_reference_cells_boxplot.png).

## A historical visualization

[![Model estimates for pigment cell groups, by gene and time](expression_of_genes_in_pigment_cells_over_time.png)](expression_of_genes_in_pigment_cells_over_time.png)

The original project figure retains the title and axes of the academic submission. Open the image to enlarge the labels, and read the note below to distinguish the calculation from its original interpretation.

## Provenance and limitations of this figure

The [Saunders_rep.Rmd notebook](https://github.com/dasesteves/projeto/blob/ce928997ab677c6ab3442ca9221aebfedb1f158b/Scripts/Saunders%20Rep/Saunders_rep.Rmd#L223) documents the calculation:

1. **Input:** `zperturb_beta_bin_results_broadtype_clean.csv`. The compressed copy stored in the project is identical to the [source from the study by Saunders and colleagues](https://github.com/cole-trapnell-lab/sdg-zfish/blob/4fa0bf88dc642b58f1b2a3b7789143e3f44a824a/data/zperturb_beta-bin_results_broadtype_clean.csv.gz). It contains differential cell abundance model results, not an RNA count matrix.
2. **Selection and calculation:** groups whose `cell_group` name contains `phore` or `pigmented`, ignoring case; mean of `estimate` by `gene1` and `timepoint`. This block does not explicitly filter for transcription factors.
3. **Output:** a line-and-point plot, with time ordered numerically and a colour for each `gene1`. The code saves `output/expression_of_genes_in_pigment_cells_over_time.png` at 10 × 10 inches and 1200 dpi. The name and resolution match the published figure; the copies in `Results` and the paper sources are identical.

**How to read it:** the original axis says “Mean Expression”, but the calculated value is the mean of beta-binomial estimates. It is not mean gene expression calculated directly from RNA counts. The [study's source code](https://github.com/cole-trapnell-lab/sdg-zfish/blob/4fa0bf88dc642b58f1b2a3b7789143e3f44a824a/figure_code/Saunders_Srivatsan_2023_Fig3.R#L69) identifies these data as differential cell abundance results.

**Contribution and limitations:** Diogo Esteves's project uses data and code from the study by Saunders and colleagues; the [final paper is co-authored by Diogo Esteves and David Henriques](https://github.com/dasesteves/projeto/blob/ce928997ab677c6ab3442ca9221aebfedb1f158b/LateX%20files/Artigo%20Final.tex#L18). This note documents the provenance found in the sources. The aggregation has since been rerun in the separate workflow and compared with the original calculation. The original academic execution environment is not recorded, and the biological interpretation of aggregating these estimates has not been validated. The historical image and paper remain unchanged.

## Browse all figures

- **Other views of the historical visualizations:** [time plot](expression_of_genes_in_pigment_cells_over_time.png), [bar chart](top_10_genes_expressed_in_pigment_cells.png) and [animation](gene_expression_evolution.gif).
- **Pigment cell UMAPs:** [18 h](umap_pigment_cells_18h.png), [24 h](umap_pigment_cells_24h.png), [36 h](umap_pigment_cells_36h.png), [48 h](umap_pigment_cells_48h.png) and [72 h](umap_pigment_cells_72h.png).
- **Other UMAP projections:** [24 h](fig_umap_24h.png), [48 h](fig_umap_48h.png) and [72 h](fig_umap_72h.png).
- **Reference cells:** [bar chart](fig1_reference_cells_barplot.png) and [boxplot](fig2_reference_cells_boxplot.png).
- **Variance:** [comparison across time points](variancia_tempos.png) and [overall boxplot](varianciatotal_boxplot.png).

These files remain as originally published in the project. Some figures have small labels and points at browser scale; open the original image to enlarge them. This gallery helps readers navigate the materials; it adds no results or scientific validation.

[Back to the project](../README.en.md) · [Scripts and reproduction requirements](../Scripts/README.en.md)
