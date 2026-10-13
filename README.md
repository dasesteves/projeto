# Células de pigmentação de peixe-zebra

Projeto académico de análise e visualização de transcriptómica de célula única, desenvolvido por **Diogo Esteves** no mestrado em Bioinformática da Universidade do Minho. O trabalho explora linhagens celulares e a expressão de marcadores associados à diferenciação das células de pigmentação.

[**Ler o artigo final**](Artigo%20Final.pdf) · [Ver os resultados](Results/) · [Consultar os scripts](Scripts/)

## Uma das visualizações

<a href="Results/expression_of_genes_in_pigment_cells_over_time.png">
<img src="Results/expression_of_genes_in_pigment_cells_over_time.png" alt="Visualização histórica de estimativas de um modelo para grupos celulares pigmentares, por gene e tempo" width="600">
</a>

*Figura histórica do projeto. O cálculo usa estimativas de um modelo beta-binomial; consulta a [origem e os limites desta figura](Results/#origem-e-limites-desta-figura) antes de interpretar o título e os eixos originais.*

## Explorar o trabalho

- [Resultados](Results/): figuras históricas, projeções UMAP e comparações entre tempos, com uma nota de proveniência para a figura acima.
- [Scripts e condições de reprodução](Scripts/): código em R e notebooks, com as dependências e os limites conhecidos.
- [Fontes do artigo](LateX%20files/) e [entrega da primeira fase](Phase%201/).

A apresentação não está disponível: o ficheiro PPTX guardado contém apenas dois bytes e não é uma apresentação válida. Para consultar a entrega, usa o artigo final acima.

As figuras e o artigo são os materiais históricos do trabalho. A análise não foi reexecutada nesta revisão da documentação; os scripts não constituem um ambiente de reprodução fechado.

<details>
<summary>Contexto académico e descrição original</summary>

## 1st year of Master Degree in Bioinformatics

- **Name:** Diogo Esteves
- **Student:** PG28935

## Course - Project

- **Professor:** Miguel Rocha

## Project Description

- **Advisor:** David Henriques – CSIC IIM (Vigo, Spain)
- **Title:** Visualization of Single-Cell Transcriptomics from Zebrafish Pigment Cells

### Abstract

This project utilizes single-cell transcriptomics techniques to investigate cell type lineages and visualize key genetic markers of pigment cell differentiation. With tools such as Monocle and Slingshot, we aim to deepen our understanding of cell proliferation and the factors influencing the pigmentation of zebrafish.

### Objectives

1. Identify cell type lineages in zebrafish single-cell transcriptomics.
2. Visualize key genetic markers of pigment cell differentiation.

## Future Work

- Explore additional single-cell RNA sequencing datasets.
- Integrate more advanced visualisation tools.
- Collaborate with other research groups for comparative studies.

## Software Used

- **R:** [Access R](https://www.r-project.org/)
- **RStudio:** [Access RStudio](https://www.rstudio.com/)
- **Monocle:** [Access Monocle](https://cole-trapnell-lab.github.io/monocle-release/)
- **Slingshot:** [Access Slingshot](https://bioconductor.org/packages/devel/bioc/vignettes/slingshot/inst/doc/vignette.html)
- **Seurat:** [Access Seurat](https://satijalab.org/seurat/)

## Acknowledgements

I would like to express my gratitude to my advisor, David Henriques, for his support and guidance throughout this project, and Professor Miguel for making it available to me.

## Project Structure

- **Apresentação_Projeto_PG28935.pptx:** Historical placeholder for the 2nd phase presentation; the two-byte file is not a valid PPTX.
- **LateX files:** Contains LaTeX files and images for the final article.
- **Phase 1:** Contains the final files from phase 1 project delivery.
- **Results:** Contains visualisation results of the analysis.
- **Scripts:** Contains scripts used for data processing, analysis, and visualisation.

</details>
