"""
omni_parse.py — OMNI2 hourly .dat files -> clean CSV

Usage: put omni2_YYYY.dat files from NASA SPDF
(https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/) in ./omni/,
then run:  python omni_parse.py

Output: omni_clean.csv with hourly solar wind, Kp, F10.7, sunspot number.
Requires: pandas, numpy
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path("omni")
OUT_CSV = "omni_clean.csv"

# OMNI2 hourly field order (see omni2.text in the same SPDF directory)
COLS = [
    'year', 'doy', 'hour', 'bartels',
    'imf_sc', 'sw_sc', 'n_imf', 'n_sw',
    'b_scalar', 'b_magnitude',
    'lat_angle', 'long_angle',
    'bx_gse', 'by_gse', 'bz_gse', 'by_gsm', 'bz_gsm',
    'sigma_b_scalar', 'sigma_b_vector', 'sigma_bx', 'sigma_by', 'sigma_bz',
    'temp', 'density', 'speed', 'flow_long', 'flow_lat', 'na_np',
    'flow_pressure', 'sigma_t', 'sigma_n', 'sigma_v', 'sigma_phi',
    'sigma_theta', 'sigma_nanp', 'electric_field', 'plasma_beta',
    'alfven_mach',
    'kp', 'sunspot', 'dst', 'ae',
    'pf_1mev', 'pf_2mev', 'pf_4mev', 'pf_10mev', 'pf_30mev', 'pf_60mev',
    'pf_flag', 'ap', 'f107', 'pcn', 'al', 'au', 'ms_mach', 'q_index',
    'lt', 'f107_adj',
]

# OMNI fill values -> NaN
NA_VALUES = [9999.99, 999.99, 999.90, 99999.9, 99999.99, 9999999.0, 999999.0, 999.999, 9999.9, 99999.0]

KEEP = ['bz_gsm', 'speed', 'density', 'temp', 'b_magnitude',
        'kp', 'f107', 'sunspot']


def load_year(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, delim_whitespace=True, names=COLS,
                     na_values=NA_VALUES, low_memory=False)
    print(f"{path.name}: {len(df)} rows")
    return df


def main() -> None:
    # read and stack all yearly files
    frames = [load_year(p) for p in sorted(DATA_DIR.glob("omni2_*.dat"))]
    df = pd.concat(frames, ignore_index=True)

    # build timestamps (year + day-of-year + hour) and sort
    df['timestamp'] = (pd.to_datetime(df['year'], format='%Y')
                       + pd.to_timedelta(df['doy'] - 1, unit='D')
                       + pd.to_timedelta(df['hour'], unit='h'))
    df = df.set_index('timestamp').sort_index()

    # every complete year must have 8760h (8784 leap); last year may be partial
    full_years = df[df['year'] < df['year'].max()]
    assert full_years.groupby('year').size().between(8760, 8784).all(), \
        "bad row count — check .dat files"
    df = df[~df.index.duplicated(keep='first')]

    # Kp is stored in tenths in some releases; clip the 9o top-code
    if df['kp'].max() > 9:
        df['kp'] = df['kp'] / 10.0
    df['kp'] = df['kp'].clip(upper=9.0)

    out = df[KEEP].copy()

    # self-check: bz mean ~0, speed ~430, kp 0..9 mean ~2;
    # deviations mean a fill value leaked — add it to NA_VALUES
    print("\n===== SELF-CHECK =====")
    for c in KEEP:
        s = out[c].dropna()
        print(f"{c:12s} n={len(s):8d}  min={s.min():10.2f}  "
              f"max={s.max():10.2f}  mean={s.mean():10.2f}")

    out.to_csv(OUT_CSV)
    print(f"\nSaved {OUT_CSV}: {len(out)} rows")


if __name__ == '__main__':
    main()