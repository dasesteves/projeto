# Saunders Rep

## Description

This folder contains scripts and data related to repetition of Saunders *et al*. (2023) initial pipeline using `monocle`

## Contents

- **Saunders_rep.html:** HTML output of the R Markdown analysis.
- **Saunders_rep.Rmd:** R Markdown script for the analysis.

## Usage

Read the saved [HTML output](Saunders_rep.html) to inspect the existing analysis. To attempt a new run, open [Saunders_rep.Rmd](Saunders_rep.Rmd) in RStudio and first review its setup and download sections.

The notebook uses this folder as its working directory, with `data/` for inputs and `output/` for generated figures. Ensure those directories and the required inputs exist before running the relevant chunks.

The download block points to `Projeto_utils.R` at the repository root, while the file is stored at [data/Projeto_utils.R](data/Projeto_utils.R). Use the local copy at the path loaded by `source("data/Projeto_utils.R")`.

## Notes

The setup installs packages and fetches Monocle 3 from its `master` branch; versions are not pinned. Running all chunks can therefore install software and download data. Record the actual environment with `sessionInfo()` for any new analysis. This documentation review did not execute the notebook or confirm that it runs from a clean session.
