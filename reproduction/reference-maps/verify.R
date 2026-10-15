args <- commandArgs(TRUE)
stopifnot(length(args)==3)
.libPaths(c(normalizePath(args[1]),.Library),include.site=FALSE)
library(data.table)
src <- fread(args[2],select=c('cell','timepoint','umap3d_1','umap3d_2','umap3d_3'))
out <- args[3]
export <- fread(file.path(out,'reference-coordinates.csv'))
stopifnot(nrow(src)==nrow(export),!anyDuplicated(src$cell),identical(src$cell,export$cell))
stopifnot(identical(export$source_row,seq_len(nrow(src))))
stopifnot(identical(src$timepoint,export$timepoint))
for(k in c('umap3d_1','umap3d_2','umap3d_3')) {
  stopifnot(all(is.finite(src[[k]])),identical(src[[k]],export[[k]]))
}
stopifnot(identical(export$map_eligible,!is.na(src$timepoint)))
counts <- fread(file.path(out,'cells-by-time.csv'))
actual <- src[,.(cells=.N),by=timepoint]
setorder(counts,timepoint);setorder(actual,timepoint)
stopifnot(identical(counts$timepoint,actual$timepoint),identical(counts$cells,actual$cells))
stopifnot(sum(counts$cells)==nrow(src),sum(is.na(src$timepoint))==85130)
maps <- fread(file.path(out,'map-membership-summary.csv'))
stopifnot(identical(maps$timepoint,c(18L,24L,36L,48L,72L)))
for(i in seq_len(nrow(maps))) {
  stopifnot(maps$highlight_cells[i]==sum(src$timepoint==maps$timepoint[i],na.rm=TRUE),
            maps$background_cells[i]==sum(!is.na(src$timepoint)),
            maps$excluded_missing_time[i]==sum(is.na(src$timepoint)))
}
writeLines(c('PASS: all cell IDs and order; all three coordinates exactly match parsed source values.',
             'PASS: all temporal counts, NA membership and five map selections independently checked in R.',
             paste('Cells:',nrow(src)),paste('Background:',sum(!is.na(src$timepoint))),
             'No CDS comparison or historical image equivalence claimed.'),file.path(out,'independent-validation.txt'))
capture.output(sessionInfo(),file=file.path(out,'validation-session.txt'))
cat('Independent R verification passed\n')
