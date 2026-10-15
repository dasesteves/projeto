library(Seurat)
library(data.table)
library(dplyr)
# Same reads, filter and constructor as the notebook; input paths relocated only.
cell_metadata <- fread(file.path(Sys.getenv('REPRO_INPUT'), 'reference_cell_metadata.csv'))
pigment_keywords <- c('phore', 'pigmented')
pigment_cells_groups <- unique(cell_metadata$cell_type_broad[grepl(paste(pigment_keywords, collapse='|'), cell_metadata$cell_type_broad, ignore.case=TRUE)])
pigment_cells_metadata <- cell_metadata %>% filter(cell_type_broad %in% pigment_cells_groups)
rm(cell_metadata)
gc()
raw_counts <- readRDS(file.path(Sys.getenv('REPRO_INPUT'), 'reference_raw_counts.RDS'))
pigment_cells_counts <- raw_counts[, pigment_cells_metadata$cell, drop=FALSE]
rm(raw_counts)
gc()
# Original constructor and preprocessing calls; no cell filtering or UMAP.
seurat_object <- CreateSeuratObject(counts=pigment_cells_counts, meta.data=pigment_cells_metadata)
expected_ids <- pigment_cells_metadata$cell
expected_meta <- seurat_object[[]]
rm(pigment_cells_counts, pigment_cells_metadata)
gc()
stages <- list()
check_stage <- function(object, stage) {
    stopifnot(identical(colnames(object), expected_ids), identical(object[[]], expected_meta))
    stages[[stage]] <<- data.frame(stage=stage, cells=ncol(object), genes=nrow(object),
        missing_timepoint=sum(is.na(object[[]]$timepoint)), ids_preserved=TRUE,
        object_bytes=as.numeric(object.size(object)))
    write.csv(do.call(rbind, stages), 'pca-stage-checks.csv', row.names=FALSE)
    cat("STAGE", stage, "verified\n")
    flush.console()
}
check_stage(seurat_object, 'constructed')
# Capture defaults from the installed methods, not presumed historical versions.
capture.output(lapply(list(NormalizeData.default=Seurat:::NormalizeData.default,
    FindVariableFeatures.default=Seurat:::FindVariableFeatures.default,
    ScaleData.default=Seurat:::ScaleData.default, RunPCA.default=Seurat:::RunPCA.default),
    formals), file='pca-installed-defaults.txt')
seurat_object <- NormalizeData(seurat_object)
check_stage(seurat_object, 'normalized')
normalized <- LayerData(seurat_object, layer='data')
counts <- LayerData(seurat_object, layer='counts')
stopifnot(all(is.finite(normalized@x)), all(normalized@x >= 0))
# Independent numerical check for deterministic sample of columns.
chosen <- unique(round(seq(1,ncol(counts),length.out=20)))
expected <- log1p(t(t(counts[,chosen,drop=FALSE]) / Matrix::colSums(counts)[chosen]) * 10000)
error <- max(abs(expected - normalized[,chosen,drop=FALSE]))
stopifnot(error < 1e-10)
write.csv(data.frame(sampled_cells=length(chosen), max_error=error), 'normalization-check.csv', row.names=FALSE)
rm(normalized, counts, expected)
gc()
seurat_object <- FindVariableFeatures(seurat_object, selection.method="vst", nfeatures=1000)
check_stage(seurat_object, 'variable_features')
stopifnot(length(VariableFeatures(seurat_object)) == 1000,
          !anyDuplicated(VariableFeatures(seurat_object)))
writeLines(VariableFeatures(seurat_object), 'pca-variable-features.txt')
seurat_object <- ScaleData(seurat_object, features=rownames(seurat_object))
check_stage(seurat_object, 'scaled')
gc()
seurat_object <- RunPCA(seurat_object, features=VariableFeatures(object=seurat_object), npcs=20)
check_stage(seurat_object, 'pca')
emb <- Embeddings(seurat_object, 'pca')
load <- Loadings(seurat_object, 'pca')
stopifnot(identical(rownames(emb), expected_ids), ncol(emb)==20,
          all(is.finite(emb)), all(is.finite(load)), all(is.finite(Stdev(seurat_object,'pca'))))
write.csv(data.frame(component=seq_len(20), standard_deviation=Stdev(seurat_object,'pca')),
    'pca-components.csv', row.names=FALSE)
write.csv(data.frame(variable_genes=1000, loading_genes=nrow(load),
    cells=nrow(emb), components=ncol(emb), finite=TRUE), 'pca-result.csv', row.names=FALSE)
# Preserve the newly calculated PCA only, clearly separate from academic results.
saveRDS(list(embeddings=emb, loadings=load, stdev=Stdev(seurat_object,'pca'),
    variable_features=VariableFeatures(seurat_object), metadata=expected_meta),
    'isolated-global-pca.rds')
capture.output(sessionInfo(), file='pca-session-info.txt')
print(read.csv('pca-result.csv'))
