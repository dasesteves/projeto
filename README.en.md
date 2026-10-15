[Português](README.md) · **English**

# Zebrafish pigment cells

An academic project on single-cell transcriptomics analysis and visualization, developed by **Diogo Esteves** during the master's degree in Bioinformatics at the University of Minho. The project explores cell lineages and markers associated with pigment cell differentiation.

[**Read the final paper**](Artigo%20Final.pdf) · [View results](Results/README.en.md) · [Explore scripts](Scripts/README.en.md) · [**Run the reproduction workflow**](reproduction/README.md)

To generate the **four model-estimate and cell-abundance variability plots**, with auditable tables, follow the [dedicated module](reproduction/README.md#gráficos-das-estimativas-e-da-abundância-celular) (instructions in Portuguese). Outputs are created locally and do not replace the academic figures.

To count cells by time and draw coordinates already supplied by the study, use the [reference counts and maps module](reproduction/README.md#contagens-e-mapas-da-referência) (instructions in Portuguese). It generates six PNG and three CSV files locally. These maps share a common reference; they are not the UMAPs recalculated separately by time in the pigment-cell subset.

To generate the [time/Oligo boxplot and verification tables](reproduction/README.md#boxplot-por-tempo-e-oligo), follow the separate workflow (instructions in Portuguese). It explains how to obtain the reference object containing `Oligo` (4.23 GB) and generates two figures and five tables locally, with the historical filters and a comparison without the scale cut. It requires no PCA/UMAP and does not replace the academic figure.

## Authorship and sources

The final paper is co-authored by **Diogo Esteves and David Henriques**. David Henriques (CSIC IIM, Vigo) supervised the project, undertaken in the Project course with **Professor Miguel Rocha**.

The work uses data and code from **Saunders and colleagues**; the paper identifies the public series [GSE202639](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202639). The academic analyses and visualizations collected here do not represent the generation of those data. The [provenance note](Results/README.en.md#provenance-and-limitations-of-this-figure) distinguishes the source data, calculation and limitations of the featured figure.

## One of the visualizations

<a href="Results/expression_of_genes_in_pigment_cells_over_time.png">
<img src="Results/expression_of_genes_in_pigment_cells_over_time.png" alt="Historical visualization of model estimates for pigment cell groups, by gene and time" width="600">
</a>

*Historical project figure. The calculation uses beta-binomial model estimates; read the [provenance and limitations](Results/README.en.md#provenance-and-limitations-of-this-figure) before interpreting the original title and axes.*

## Explore the work

- [Results](Results/README.en.md): historical figures, UMAP projections and comparisons across time points, with a provenance note for the figure above.
- [Scripts and reproduction requirements](Scripts/README.en.md): R code and notebooks, dependencies and known limitations.
- [Paper sources](LateX%20files/) and [first-phase submission](Phase%201/).

The presentation is unavailable: the stored PPTX contains only two bytes and is not a valid presentation. Use the final paper linked above to consult the submission.

The historical figures and paper are preserved. A [separate reproduction workflow](reproduction/) provides verified inputs and pinned versions for aggregation, global PCA and five UMAPs (instructions in Portuguese). It does not cover every project method or establish numerical equivalence with the historical figures.

[Original academic description and acknowledgements (expand the section in the Portuguese README)](README.md) · [Diogo Esteves's profile](https://github.com/dasesteves/dasesteves/blob/main/README.en.md)
