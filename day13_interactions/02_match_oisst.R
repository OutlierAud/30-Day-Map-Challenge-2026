library(readr)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3L) {
  stop("Usage: Rscript 02_match_oisst.R TRACKS.csv MATCHED.csv OISST.nc [OISST.nc ...]", call. = FALSE)
}
tracks <- read_csv(args[1], show_col_types = FALSE)
result <- tracks
result$sst_c <- NA_real_
result$sst_grid_lat <- NA_real_
result$sst_grid_lon <- NA_real_
result$sst_source <- NA_character_
covered <- rep(FALSE, nrow(tracks))
seen_dates <- as.Date(character())

for (path in args[-(1:2)]) {
  dump <- system2("ncdump", c("-v", "time,latitude,longitude,sst", shQuote(path)), stdout = TRUE)
  stopifnot(is.null(attr(dump, "status")))
  stopifnot(any(grepl('sst:units = "degree_C"', dump, fixed = TRUE)))
  stopifnot(any(grepl(
    'time:units = "seconds since 1970-01-01[ T]00:00:00( ?UTC|Z)?"', dump
  )))
  data_start <- match("data:", dump)
  stopifnot(!is.na(data_start))
  body <- paste(dump[seq.int(data_start + 1L, length(dump))], collapse = "\n")
  read_variable <- function(name) {
    pattern <- paste0("\\b", name, "\\s*=\\s*([^;]+);")
    hit <- regmatches(body, regexec(pattern, body, perl = TRUE))[[1]]
    stopifnot(length(hit) == 2L)
    scan(text = gsub(",", " ", hit[2], fixed = TRUE), na.strings = "_", quiet = TRUE)
  }

  times <- as.POSIXct(read_variable("time"), origin = "1970-01-01", tz = "UTC")
  dates <- as.Date(times, tz = "UTC")
  latitudes <- read_variable("latitude")
  longitudes <- read_variable("longitude")
  values <- read_variable("sst")
  stopifnot(
    length(values) == length(longitudes) * length(latitudes) * length(dates),
    length(dates) > 0L, !anyNA(dates), !anyDuplicated(dates),
    !any(dates %in% seen_dates),
    identical(latitudes, seq(19.875, 45.125, by = .25)),
    identical(longitudes, seq(119.875, 150.125, by = .25)),
    all(is.na(values) | (is.finite(values) & values >= -3 & values <= 45))
  )
  seen_dates <- c(seen_dates, dates)
  temperatures <- array(values, c(length(longitudes), length(latitudes), length(dates)))
  time_index <- match(tracks$sst_date_utc, dates)
  rows <- which(!is.na(time_index))
  lat_index <- vapply(tracks$lat[rows], function(lat) which.min(abs(latitudes - lat)), integer(1))
  lon_index <- vapply(tracks$lon[rows], function(lon) which.min(abs(longitudes - lon)), integer(1))
  result$sst_grid_lat[rows] <- latitudes[lat_index]
  result$sst_grid_lon[rows] <- longitudes[lon_index]
  result$sst_c[rows] <- round(temperatures[cbind(lon_index, lat_index, time_index[rows])], 2)
  # Preserve archive provenance using the original ERDDAP download filenames.
  archive <- if (startsWith(basename(path), "ncdcOisst21NrtAgg_")) {
    "near-real-time"
  } else if (startsWith(basename(path), "ncdcOisst21Agg_")) {
    "final"
  } else {
    stop("Expected an original ERDDAP download filename: ", path)
  }
  result$sst_source[rows] <- paste0("NOAA OISST v2.1 (ERDDAP ", archive, " archive)")
  covered[rows] <- TRUE
}

result$sst_match_status <- ifelse(!covered, "date_unavailable",
                                   ifelse(is.na(result$sst_c), "grid_cell_masked", "matched"))
write_csv(result, args[2])
print(with(result, table(year, sst_match_status)))
print(with(subset(result, in_jun_sep), table(year, sst_match_status)))
if (any(is.finite(result$sst_c))) {
  print(range(result$sst_c, na.rm = TRUE))
}
