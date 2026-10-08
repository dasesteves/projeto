# Scripts

## Description

This folder contains all the scripts used for data processing, analysis, and visualization related to the single-cell transcriptomic analysis of zebrafish pigment cells.

## Contents

- **analise_remota_scripts.Rmd:** Script for remote analysis of single-cell transcriptomics data.
- **memory_optimization_scripts.Rmd:** Script focused on memory optimization techniques for handling large single-cell RNA-seq datasets.
- **UMAP_simple.Rmd:** Script for performing UMAP dimensionality reduction on single-cell RNA-seq data.
- **[Saunders Rep](Saunders%20Rep/):** Notebook, saved HTML output and supporting files for the Saunders analysis.

## Usage

These are analysis notebooks, with no single execution order documented for the whole folder. Read the setup and data-loading sections of the notebook you intend to use.

- `UMAP_simple.Rmd` installs R and Python packages, downloads GEO data and uses the active RStudio document to set the working directory. It references `raw_counts` without loading that object, and inspects `cell_metadata` before its loading section. It therefore needs preparation before execution in a fresh session.
- The [Saunders notebook](Saunders%20Rep/) uses relative `data/` and `output/` paths. Its README records the working-directory and dependency requirements.
- The repository has no `renv.lock` or other file fixing the R package versions. Record `sessionInfo()` when reproducing an analysis; the original package versions are not established here.

This documentation review did not rerun the analyses or validate the historical results.

## Notes

- Ensure you have the necessary computational resources, as some scripts may require significant memory and processing power.
- Refer to the individual script headers for specific instructions and details.
