#bioconductor install
if (!require("BiocManager", quietly = TRUE))
  install.packages("BiocManager")
BiocManager::install()
BiocManager::valid() 
BiocManager::install(c(
  "digest", "glue", "rlang"
), update = TRUE, ask = FALSE, force = TRUE)



#monocle 3 install
source("http://bioconductor.org/biocLite.R")
biocLite()
biocLite("monocle")
devtools::install_github("cole-trapnell-lab/DDRTree", ref="simple-ppt-like")
devtools::install_github("cole-trapnell-lab/L1-graph")
install.packages("reticulate")
library(reticulate)
py_install('umap-learn', pip = T, pip_ignore_installed = T) # Ensure the latest version of UMAP is installed
py_install("louvain")
devtools::install_github("cole-trapnell-lab/monocle-release", ref="monocle3_alpha")