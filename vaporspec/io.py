# io.py
import numpy as np
import xarray as xr
import pandas as pd


# Boulder bounding box
BOULDER_DOMAIN = dict(
    north=40.1,
    south=39.9,
    west=-105.3,
    east=-104.9
)

def load_cu_atoc(path):
    """Load CU ATOC station CSV."""
    df = pd.read_csv(path, parse_dates=["time"])
    return df


def load_era5(pressure_file, singlelevel_file, radiation_file, subset_to_boulder=True):
    p = xr.open_dataset(pressure_file)
    s = xr.open_dataset(singlelevel_file)
    r = xr.open_dataset(radiation_file)

    # Pressure-level
    q850 = p["q"].sel(pressure_level=850)
    t850 = p["t"].sel(pressure_level=850)

    # Single-level
    sp  = s["sp"]
    tcc = s["tcc"]

    # Radiation
    strd = r["strd"]   # downwelling
    str_net = r["str"] # net LW

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
    return era


def merge_cu_era5(cu, era):
    """
    Merge CU ATOC dataframe with ERA5 dataset.
    - Convert CU ATOC to UTC
    - Rename ERA5 valid_time
    - Inner merge on exact timestamps
    """
    cu = cu.copy()
    cu["time_utc"] = cu["time"] + pd.Timedelta(hours=6)

    df_era = era.to_dataframe().reset_index()
    df_era = df_era.rename(columns={"valid_time": "time_utc"})

    merged = cu.merge(df_era, on="time_utc", how="inner")
    return merged


def compute_surface_specific_humidity(df):
    """
    Compute surface specific humidity from dewpoint and surface pressure.
    Matches original notebook.
    """
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



def filter_clear_sky(df):
    """Filter rows where total cloud cover < 0.3."""
    return df[df["tcc"] < 0.3]


def prepare_lw_down_map(era):
    """
    Extract lon, lat, LW↓ monthly mean for mapping.
    """
    lw = era["strd"]
    time_dim = "time" if "time" in lw.dims else "valid_time"
    lw_mean = lw.mean(dim=time_dim)

    lon = lw_mean["longitude"].values
    lat = lw_mean["latitude"].values
    LW  = lw_mean.values

    lon_min = float(lon.min())
    lon_max = float(lon.max())
    lat_min = float(lat.min())
    lat_max = float(lat.max())

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

