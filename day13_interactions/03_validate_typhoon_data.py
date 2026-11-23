"""Validate the raw NOAA files and generate both processed track CSVs."""

import argparse
from pathlib import Path
import subprocess


def process_sources(ibtracs, oisst_files, output_dir):
    script_dir = Path(__file__).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)
    tracks = output_dir / "typhoon_tracks_2024_2026.csv"
    matched = output_dir / "typhoon_tracks_oisst_2024_2026.csv"

    subprocess.run(
        ["Rscript", script_dir / "01_prepare_tracks.R", ibtracs, tracks],
        check=True,
    )
    subprocess.run(
        ["Rscript", script_dir / "02_match_oisst.R", tracks, matched, *oisst_files],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ibtracs", type=Path, required=True, help="Raw IBTrACS CSV")
    parser.add_argument("--oisst", type=Path, nargs="+", required=True, help="Raw OISST NetCDF files")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for the two CSVs")
    args = parser.parse_args()

    for path in [args.ibtracs, *args.oisst]:
        if not path.is_file():
            parser.error(f"Input file does not exist: {path}")
    process_sources(args.ibtracs, args.oisst, args.output_dir)


if __name__ == "__main__":
    main()
