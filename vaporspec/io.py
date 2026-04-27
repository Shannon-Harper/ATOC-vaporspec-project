# io.py
"""
Data loading and preprocessing utilities for vaporspec.

This module handles:
- loading CU ATOC station data
- loading ERA5 pressure-level, single-level, and radiation datasets
- merging CU ATOC with ERA5
- computing surface specific humidity
- filtering clear-sky conditions
- preparing LW↓ maps for plotting
"""

import numpy as np
import xarray as xr
import pandas as pd


# Boulder bounding box (used for subsetting)

BOULDER_DOMAIN = dict(
    north=40.1,
    south=39.9,
    west=-105.3,
    east=-104.9
)


# Load CU ATOC station CSV

def load_cu_atoc(path):
    """Load CU ATOC station CSV file."""
    df = pd.read_csv(path, parse_dates=["time"])   # parse timestamps
    
    required = ["time", "Dew_Out_C", "Pressure_hPa"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required CU ATOC columns: {missing}")

    return df


# Load ERA5 datasets

def load_era5(pressure_file, cloud_file, radiation_file, subset_to_boulder=True):
    """Load ERA5 pressure-level, surface-tcc, and radiation datasets."""
    p = xr.open_dataset(pressure_file)
    s = xr.open_dataset(cloud_file)
    r = xr.open_dataset(radiation_file)

    # Pressure-level variables
    q850 = p["q"].sel(pressure_level=850)          # specific humidity at 850 hPa
    t850 = p["t"].sel(pressure_level=850)          # temperature at 850 hPa

    # Single-level variables
    sp  = s["sp"]                                  # surface pressure
    tcc = s["tcc"]                                 # total cloud cover

    # Radiation variables
    strd = r["strd"]                               # downwelling LW
    str_net = r["str"]                             # net LW

    # Combine into one dataset
    era = xr.Dataset(
        dict(
            q850=q850,
            t850=t850,
            sp=sp,
            tcc=tcc,
            strd=strd,
            str=str_net,
        )
    )

    if subset_to_boulder:
        era = era.sel(
            latitude=slice(BOULDER_DOMAIN["south"], BOULDER_DOMAIN["north"]),
            longitude=slice(BOULDER_DOMAIN["west"], BOULDER_DOMAIN["east"]),
        )

    return era


# Merge CU ATOC with ERA5

def merge_cu_era5(cu, era):
    """Merge CU ATOC dataframe with ERA5 dataset on matching UTC timestamps."""
    cu = cu.copy()
    cu["time_utc"] = cu["time"] + pd.Timedelta(hours=6)   # convert local → UTC

    df_era = era.to_dataframe().reset_index()             # flatten ERA5
    df_era = df_era.rename(columns={"valid_time": "time_utc"})

    merged = cu.merge(df_era, on="time_utc", how="inner") # exact timestamp match
    return merged


# Compute surface specific humidity

def compute_surface_specific_humidity(df):
    """Compute surface specific humidity from dewpoint and surface pressure."""
    if "Dew_Out_C" not in df or "Pressure_hPa" not in df:
        raise ValueError("Dew_Out_C and Pressure_hPa must be present.")
    
    Td = df["Dew_Out_C"]
    p  = df["Pressure_hPa"]

    # Vapor pressure (Pa)
    e = 6.112 * np.exp((17.67 * Td) / (Td + 243.5))

    # Convert hPa → Pa
    p_pa = p * 100

    # Specific humidity (kg/kg)
    q_surface = 0.622 * e / (p_pa - 0.378 * e)

    df["q_surface"] = q_surface
    return df


# Clear-sky filter

def filter_clear_sky(df, threshold=0.3):
    """
    Filter rows where total cloud cover < threshold.
    Adds a 'cloud_mask' column:
        1 = clear‑sky
        0 = cloudy
    """
    if "tcc" not in df:
        raise ValueError("Column 'tcc' (total cloud cover) is required.")

    df = df.copy()
    df["cloud_mask"] = (df["tcc"] < threshold).astype(int)
    return df[df["cloud_mask"] == 1]



# Prepare LW↓ map fields

def prepare_lw_down_map(era):
    """Extract lon, lat, and LW↓ monthly mean for mapping."""
    lw = era["strd"]
    time_dim = "time" if "time" in lw.dims else "valid_time"   # handle ERA5 variants
    lw_mean = lw.mean(dim=time_dim)                            # monthly mean

    lon = lw_mean["longitude"].values
    lat = lw_mean["latitude"].values
    LW  = lw_mean.values

    # Boulder coordinates
    boulder_lon = -105.27
    boulder_lat = 40.015

    # Find nearest ERA5 grid point
    lon_idx = (abs(lon - boulder_lon)).argmin()
    lat_idx = (abs(lat - boulder_lat)).argmin()

    # Compute ERA5 grid cell boundaries (1° grid)
    lon_center = lon[lon_idx]
    lat_center = lat[lat_idx]

    lon_min = lon_center - 0.5
    lon_max = lon_center + 0.5
    lat_min = lat_center - 0.5
    lat_max = lat_center + 0.5

    return lon, lat, LW, lon_min, lon_max, lat_min, lat_max

