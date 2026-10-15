[Português](README.md) · **English**

# Scripts

## Description

This folder contains all the scripts used for data processing, analysis, and visualization related to the single-cell transcriptomic analysis of zebrafish pigment cells.

To run aggregation, global PCA and the five UMAPs, start with the [verified reproduction workflow](../reproduction/README.md) (instructions in Portuguese). This folder preserves the academic notebooks; it is not the entry point for that workflow.

## Contents

- **analise_remota_scripts.Rmd:** Script for remote analysis of single-cell transcriptomics data.
- **memory_optimization_scripts.Rmd:** Script focused on memory optimization techniques for handling large single-cell RNA-seq datasets.
- **UMAP_simple.Rmd:** Script for performing UMAP dimensionality reduction on single-cell RNA-seq data.
- **[Saunders Rep](Saunders%20Rep/):** Notebook, saved HTML output and supporting files for the Saunders analysis.

## Usage

These are analysis notebooks, with no single execution order documented for the whole folder. Read the setup and data-loading sections of the notebook you intend to use.

- `UMAP_simple.Rmd` installs R and Python packages, downloads GEO data and uses the active RStudio document to set the working directory. It references `raw_counts` without loading that object, and inspects `cell_metadata` before its loading section. It therefore needs preparation before execution in a fresh session.
- The [Saunders notebook](Saunders%20Rep/) uses relative `data/` and `output/` paths. Its README records the working-directory and dependency requirements.
- The historical package versions for these notebooks are not established. The separate workflow pins its own [reproduction versions](../reproduction/versions.csv); these do not reconstruct the original academic environment.

The separate workflow was executed and compared with the previous modern reproduction. This does not validate all notebooks in this folder or establish numerical equivalence with the historical results.

## Notes

- Ensure you have the necessary computational resources, as some scripts may require significant memory and processing power.
- Refer to the individual script headers for specific instructions and details.

[Back to the project](../README.en.md) · [Results and limitations](../Results/README.en.md)
