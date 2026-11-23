args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2L) {
  stop("Usage: Rscript 05_extract_ocean_grids.R OUTPUT_DIR OISST.nc [OISST.nc ...]", call. = FALSE)
}
dir.create(args[1], showWarnings = FALSE)
for (path in args[-1]) {
  dump <- system2("ncdump", c("-v", "time,latitude,longitude,sst", shQuote(path)), stdout = TRUE)
  stopifnot(is.null(attr(dump, "status")), any(grepl('sst:units = "degree_C"', dump, fixed = TRUE)))
  data_start <- match("data:", dump)
  stopifnot(!is.na(data_start))
  body <- paste(dump[seq.int(data_start + 1L, length(dump))], collapse = "\n")
  variable <- function(name) {
    pattern <- paste0("\\b", name, "\\s*=\\s*([^;]+);")
    hit <- regmatches(body, regexec(pattern, body, perl = TRUE))[[1]]
    stopifnot(length(hit) == 2L)
    scan(text = gsub(",", " ", hit[2], fixed = TRUE), na.strings = "_", quiet = TRUE)
  }
  times <- variable("time")
  dates <- as.Date(as.POSIXct(times, origin = "1970-01-01", tz = "UTC"), tz = "UTC")
  stopifnot(!anyDuplicated(dates),
            identical(variable("latitude"), seq(19.875, 45.125, .25)),
            identical(variable("longitude"), seq(119.875, 150.125, .25)))
  sst <- variable("sst")
  stopifnot(length(sst) == 122L * 102L * length(dates))
  sst <- array(sst, c(122L, 102L, length(dates)))
  for (i in seq_along(dates)) {
    # Preserve one extra row and column on each edge for interpolation.
    grid <- sst[, 102:1, i]
    output <- file.path(args[1], paste0(dates[i], ".bin"))
    stopifnot(!file.exists(output))
    writeBin(as.numeric(grid), output, size = 4, endian = "little")
  }
}
