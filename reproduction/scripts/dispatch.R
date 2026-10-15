.libPaths(c(normalizePath(Sys.getenv('REPRO_LIBRARY'),mustWork=TRUE), .Library), include.site=FALSE)
kit <- Sys.getenv('REPRO_KIT')
expected <- read.csv(file.path(kit,'versions.csv'), stringsAsFactors=FALSE)
installed <- installed.packages()
actual <- installed[match(expected$Package, installed[,'Package']),'Version']
checks <- data.frame(package=expected$Package, expected=expected$Version, actual=actual,
                     matches=!is.na(actual) & actual==expected$Version)
write.csv(checks, 'package-check.csv', row.names=FALSE)
capture.output(sessionInfo(), file='environment.txt')
stopifnot(as.character(getRversion()) == '4.6.1', all(checks$matches))
stage <- Sys.getenv('REPRO_STAGE')
if (stage != 'environment') source(file.path(kit,'scripts',paste0(stage,'.R')),encoding='UTF-8')
