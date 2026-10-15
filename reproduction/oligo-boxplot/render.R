# Local candidate. Statistics reproduce the grouping/filter contract, not historical pixels.
if(sys.nframe()==0) {
 cli_args<-commandArgs(TRUE)
 if(length(cli_args)!=3)stop('Usage: Rscript --vanilla render.R <library> <metadata.csv> <new-output-dir>')
 .libPaths(c(cli_args[1],.libPaths()))
}
suppressPackageStartupMessages({library(data.table);library(ggplot2)})

audit_metadata<-function(metadata) {
 required<-c('cell','timepoint','Oligo')
 if(!all(required %in% names(metadata))) stop('Required fields: cell, timepoint, Oligo')
 d<-as.data.table(metadata)
 if(!nrow(d)||anyNA(d$cell)||any(!nzchar(d$cell))||anyDuplicated(d$cell)) stop('Cell IDs must be present and unique')
 if(!is.numeric(d$timepoint)||any(!is.finite(d$timepoint[!is.na(d$timepoint)]))) stop('Time must be numeric, finite or NA')
 if(!is.character(d$Oligo)||any(!is.na(d$Oligo)&!nzchar(d$Oligo))) stop('Oligo must be a string or explicit NA, never empty')
 g<-d[,.(cells=.N),by=.(timepoint,Oligo)]
 g[,missing_group:=is.na(timepoint)|is.na(Oligo)]
 g[,log10_cells:=log10(cells)]
 g[,historical_eligible:=!missing_group & log10_cells>=1.5 & log10_cells<=4.5]
 g[,exclusion_reason:=fifelse(missing_group,'missing_time_or_Oligo',
   fifelse(log10_cells<1.5,'below_historical_scale',fifelse(log10_cells>4.5,'above_historical_scale','included')))]
 setorder(g,timepoint,Oligo,na.last=TRUE)
 s<-g[,.(groups_before_filter=.N,cells_before_filter=sum(cells),
   groups_missing=sum(missing_group),cells_missing=sum(cells[missing_group]),
   groups_scale_excluded=sum(!missing_group & !historical_eligible),
   cells_scale_excluded=sum(cells[!missing_group & !historical_eligible]),
   groups_historical=sum(historical_eligible),cells_historical=sum(cells[historical_eligible])),by=timepoint]
 list(groups=g,summary=s)
}

make_boxplot<-function(groups,historical=TRUE) {
 d<-copy(groups[missing_group==FALSE])
 if(!nrow(d))stop('No groups with both time and Oligo')
 times<-sort(unique(d$timepoint),decreasing=TRUE)
 d[,time_label:=factor(as.character(timepoint),levels=as.character(times))]
 pal<-grDevices::colorRampPalette(c('#DF4828','#E78C35','#F6C141','#4EB265','#1965B0'))(length(times))
 names(pal)<-as.character(sort(times))
 p<-ggplot(d,aes(x=time_label,y=log10_cells,fill=time_label))+
  geom_boxplot(linewidth=.35,outlier.size=1.2,outlier.alpha=.7,width=.6)+
  scale_fill_manual(values=pal)+coord_flip()+theme_minimal(base_size=12)+
  theme(legend.position='none',panel.grid.major.y=element_blank(),panel.grid.minor=element_blank(),
    plot.title=element_text(face='bold',size=16),plot.subtitle=element_text(size=11),
    plot.caption=element_text(hjust=0,size=9,colour='#424a53'),plot.margin=margin(15,20,15,15))+
  labs(x='Tempo (hpf)',y='log10 do número de células por grupo Oligo',
   title=if(historical)'Células por tempo e Oligo | filtros históricos' else 'Células por tempo e Oligo | sem corte da escala',
   subtitle=if(historical)'Limites de 1,5 a 4,5 aplicados antes do cálculo das caixas' else 'Comparação descritiva: todos os grupos com tempo e Oligo conhecidos')
 if(historical)p<-p+scale_y_continuous(limits=c(1.5,4.5),breaks=c(1.5,2,2.5,3,3.5,4,4.5))
 p
}

box_statistics<-function(plot) {
 b<-suppressWarnings(ggplot_build(plot));d<-as.data.table(b$data[[1]])
 labels<-b$layout$panel_scales_x[[1]]$get_limits()
 if(!nrow(d))return(data.table())
 d[,timepoint:=as.numeric(labels[as.integer(x)])]
 d[,.(timepoint,ymin,lower,middle,upper,ymax,
    outlier_count=lengths(outliers),outliers_log10=vapply(outliers,function(x)paste(format(x,digits=17),collapse=';'),''))]
}

run_module<-function(input,output) {
 if(file.exists(output))stop('Output must be a new directory; no overwrites')
 if(!requireNamespace('digest',quietly=TRUE)||!requireNamespace('jsonlite',quietly=TRUE))stop('digest and jsonlite are required')
 input_hash<-digest::digest(file=input,algo='sha256')
 if(input_hash!='98884c9a9ec2433b5c001cb50ae404ca4849e508d54d59b6037eb105ad3aef53')stop('Input does not match the verified reference metadata export')
 d<-fread(input,na.strings='NA',colClasses=list(character=c('cell','Oligo')))
 a<-audit_metadata(d)
 if(!dir.create(output,recursive=TRUE))stop('Cannot create output directory')
 fwrite(a$groups,file.path(output,'groups-before-filters.csv'),na='NA')
 fwrite(a$groups[historical_eligible==FALSE],file.path(output,'excluded-groups.csv'),na='NA')
 fwrite(a$groups[historical_eligible==TRUE],file.path(output,'groups-used-historical.csv'),na='NA')
 fwrite(a$summary,file.path(output,'filter-summary-by-time.csv'),na='NA')
 missing<-sum(a$groups$cells[a$groups$missing_group]);ng<-sum(a$groups$historical_eligible)
 sg<-sum(!a$groups$missing_group & !a$groups$historical_eligible)
 sc<-sum(a$groups$cells[!a$groups$missing_group & !a$groups$historical_eligible])
 stats<-list()
 for(historical in c(TRUE,FALSE)) {
  mode<-if(historical)'historical' else 'without-scale-cut'
  p<-make_boxplot(a$groups,historical)
  cap<-paste0('Fonte: Saunders, Srivatsan et al. / GEO GSE202639. Metadados do objeto de referência.\n',
   format(missing,big.mark=' ',trim=TRUE),' células excluídas por tempo/Oligo ausente; sem imputação. ',
   if(historical) paste0(sg,' grupos (',sc,' células) excluídos pela escala; ',ng,' grupos usados.') else 'Nenhum grupo excluído pela escala.',
   '\nCaixas: quartis de log10(n); linha: mediana; bigodes: até 1,5 × IQR; pontos: valores além dos bigodes.',
   '\nContagens de células recuperadas; não estimam abundância no animal nem provam independência biológica.')
  p<-p+labs(caption=cap)
  # Removal by scale is intentional and tabulated above. Do not silence other warnings.
  withCallingHandlers(ggsave(file.path(output,paste0('boxplot-',mode,'.png')),p,width=12,height=9,dpi=180,bg='white'),
   warning=function(w) {if(grepl('Removed .*non-finite.*stat_boxplot',conditionMessage(w)))invokeRestart('muffleWarning')})
  st<-box_statistics(p);st[,mode:=mode];stats[[mode]]<-st
 }
 fwrite(rbindlist(stats),file.path(output,'box-statistics-log10.csv'),na='NA')
 writeLines(capture.output(sessionInfo()),file.path(output,'session-info.txt'))
 outputs<-list.files(output,full.names=TRUE)
 receipt<-list(status='completed',input_sha256=input_hash,
  rows=nrow(d),groups_before_filter=nrow(a$groups),cells_missing_group=missing,
  historical_groups=ng,scale_excluded_groups=sg,scale_excluded_cells=sc,
  rules=list(group_by=c('timepoint','Oligo'),missing='excluded after aggregation; never imputed',
    transform='log10(n) before quartiles',historical_scale=c(1.5,4.5),quartiles='ggplot2 unweighted quantile type 7',
    absent_zero_groups='not created',embryo='not used for grouping, filtering or imputation'),
  versions=list(R=as.character(getRversion()),ggplot2=as.character(packageVersion('ggplot2')),data.table=as.character(packageVersion('data.table'))),
  output_sha256=setNames(lapply(outputs,function(f)digest::digest(file=f,algo='sha256')),basename(outputs)),
  limits=c('No historical pixel equivalence','No biological independence inference','No expression/UMAP recalculation','Originals unchanged; not published'))
 jsonlite::write_json(receipt,file.path(output,'receipt.json'),pretty=TRUE,auto_unbox=TRUE)
 cat('Completed:',output,'\n')
}

if(sys.nframe()==0) {
 args<-commandArgs(TRUE)
 if(length(args)!=3)stop('Usage: Rscript --vanilla render.R <library> <metadata.csv> <new-output-dir>')
 run_module(args[2],args[3])
}
