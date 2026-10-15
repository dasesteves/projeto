library(Seurat)
library(ggplot2)
out <- 'umap-reproduction'
if (dir.exists(out)) stop('Output directory already exists; refusing overwrite')
dir.create(out)
pca <- readRDS(Sys.getenv('REPRO_PCA'))
stopifnot(identical(rownames(pca$embeddings), rownames(pca$metadata)),
          ncol(pca$embeddings)==20, all(is.finite(pca$embeddings)))
# The historical Seurat method extracts these PCA rows and calls RunUMAP.default.
# Pass the same matrix directly; no fake counts or reconstructed expression assay.
capture.output(Seurat:::RunUMAP.Seurat, file=file.path(out,'seurat-umap-dispatch.txt'))
capture.output(formals(Seurat:::RunUMAP.default), file=file.path(out,'umap-defaults.txt'))
colors <- c(xanthophore='yellow',erythrophore='red',iridophore='cyan',
            leucophore='white',melanophore='black',cyanophore='blue',
            'retinal pigmented epithelium (early)'='darkgray',
            'retinal pigmented epithelium (late)'='lightgray')
summary <- list()
for (time in c(18,24,36,48,72)) {
    ids <- rownames(pca$metadata)[!is.na(pca$metadata$timepoint) & pca$metadata$timepoint==time]
    input <- pca$embeddings[ids,1:20,drop=FALSE]
    # Defaults are recorded from this installed version; historical call specified dims only.
    embedding <- RunUMAP(input)
    coords <- Embeddings(embedding)
    stopifnot(identical(rownames(coords),ids), ncol(coords)==2, all(is.finite(coords)))
    saveRDS(embedding,file.path(out,paste0('umap-',time,'h.rds')))
    df <- data.frame(cell=ids, UMAP_1=coords[,1],UMAP_2=coords[,2],
                     cell_type_broad=pca$metadata[ids,'cell_type_broad'])
    write.csv(df,file.path(out,paste0('coordinates-',time,'h.csv')),row.names=FALSE)
    # Separate deterministic draw order for review; does not alter coordinates.
    set.seed(42)
    df <- df[sample.int(nrow(df)),]
    plot <- ggplot(df,aes(UMAP_1,UMAP_2,color=cell_type_broad)) +
        geom_point(stroke=0,size=0.15) + theme_void() +
        theme(legend.position='right',legend.title=element_blank(),plot.title=element_text(size=10)) +
        scale_color_manual(values=colors) + ggtitle(paste('UMAP of Pigment Cells at',time,'h'))
    ggsave(file.path(out,paste0('umap-',time,'h.png')),plot=plot,
           width=10,height=10,dpi=150,bg='white')
    summary[[as.character(time)]] <- data.frame(timepoint=time,cells=length(ids),
        components_input=ncol(input),coordinates_finite=TRUE)
}
write.csv(do.call(rbind,summary),file.path(out,'summary.csv'),row.names=FALSE)
capture.output(sessionInfo(),file=file.path(out,'session-info.txt'))
