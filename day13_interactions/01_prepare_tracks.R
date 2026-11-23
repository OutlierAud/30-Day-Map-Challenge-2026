library(readr)
library(dplyr)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2L) {
  stop("Usage: Rscript 01_prepare_tracks.R IBTRACS.csv TRACKS.csv", call. = FALSE)
}
required_columns <- c("SID", "ISO_TIME", "LAT", "LON", "USA_WIND",
                      "USA_PRES", "BASIN", "NAME", "TRACK_TYPE")
raw_tracks <- read_csv(
  args[1],
  col_types = cols_only(
    SID = col_character(),
    ISO_TIME = col_character(),
    LAT = col_character(),
    LON = col_character(),
    USA_WIND = col_character(),
    USA_PRES = col_character(),
    BASIN = col_character(),
    NAME = col_character(),
    TRACK_TYPE = col_character()
  )
)
stopifnot(all(required_columns %in% names(raw_tracks)), nrow(raw_tracks) > 1L)
stop_for_problems(raw_tracks)

tracks <- raw_tracks |>
  slice(-1) |>
  filter(BASIN == "WP", between(substr(ISO_TIME, 1, 4), "2024", "2026")) |>
  mutate(
    across(c(LAT, LON, USA_WIND, USA_PRES), ~ {
      values <- parse_double(.x)
      stop_for_problems(values)
      values
    }),
    ISO_TIME = as.POSIXct(ISO_TIME, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")
  )

stopifnot(
  nrow(tracks) > 0L,
  !anyNA(tracks$SID),
  !anyNA(tracks$ISO_TIME),
  all(is.na(tracks$LAT) | between(tracks$LAT, -90, 90)),
  all(is.na(tracks$LON) | between(tracks$LON, -180, 180)),
  all(is.na(tracks$USA_WIND) | (is.finite(tracks$USA_WIND) & tracks$USA_WIND >= 0))
)
# Missing location or wind excludes a record from the map filters.
cat("IBTrACS observations in the basin and years:", nrow(tracks), "\n")
cat("Missing latitude, longitude or wind:",
    sum(!complete.cases(tracks[c("LAT", "LON", "USA_WIND")])), "\n")
latest_basin <- max(tracks$ISO_TIME)
regional <- tracks |>
  filter(
    between(LAT, 20, 45),
    between(LON, 120, 150),
    TRACK_TYPE %in% c("main", "PROVISIONAL", "US-PROVISIONAL")
  )

prepared <- regional |>
  filter(USA_WIND >= 64) |>
  rename_with(tolower) |>
  mutate(
    year = as.integer(format(iso_time, "%Y", tz = "UTC")),
    month = as.integer(format(iso_time, "%m", tz = "UTC")),
    sst_date_utc = as.Date(iso_time, tz = "UTC"),
    in_jun_sep = between(month, 6L, 9L)
  ) |>
  select(sid, iso_time, lat, lon, year, month, usa_wind, usa_pres, basin,
         name, track_type, sst_date_utc, in_jun_sep) |>
  arrange(iso_time, sid)

stopifnot(
  nrow(prepared) > 0L,
  !anyNA(prepared$sid),
  !anyDuplicated(prepared[c("sid", "iso_time")])
)
write_csv(prepared, args[2])
print(prepared |> group_by(year) |> summarise(
  records = n(), storms = n_distinct(sid),
  summer_storms = n_distinct(sid[in_jun_sep]), summer_records = sum(in_jun_sep),
  first = min(iso_time), last = max(iso_time)
))
print(latest_basin)
