# utils.py
"""
Utility functions shared across vaporspec modules:
- Coordinate normalization and subsetting
- Plot styling
"""

import matplotlib.pyplot as plt

# Plot Style Helper

def set_plot_style():
    import seaborn as sns
    sns.set(style="whitegrid", context="talk")

    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.labelsize": 14,
        "axes.titlesize": 16,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
    })



# Robust Region Subsetting

def subset_region(ds, north, south, west, east):
    """
    Subset an xarray Dataset or DataArray to a lat/lon bounding box.

    Automatically handles:
    - lat/lon ascending or descending
    - single-point grids
    - alternate coordinate names (lat/lon, latitude/longitude, x/y)
    """

    # Normalize coordinate names

    rename_map = {}

    if "lat" in ds.coords:
        rename_map["lat"] = "latitude"
    if "lon" in ds.coords:
        rename_map["lon"] = "longitude"
    if "latitude0" in ds.coords:
        rename_map["latitude0"] = "latitude"
    if "longitude0" in ds.coords:
        rename_map["longitude0"] = "longitude"
    if "y" in ds.coords and "x" in ds.coords:
        rename_map["y"] = "latitude"
        rename_map["x"] = "longitude"

    if rename_map:
        ds = ds.rename(rename_map)

    # If dataset has no spatial dimension (subset)

    if "latitude" not in ds.coords or "longitude" not in ds.coords:
        return ds

    # Handle slice direction based on coordinate ordering

    lat_vals = ds["latitude"].values
    lon_vals = ds["longitude"].values

    # Latitude slice
    if lat_vals[0] > lat_vals[-1]:  # descending
        lat_slice = slice(north, south)
    else:                           # ascending
        lat_slice = slice(south, north)

    # Longitude slice
    if lon_vals[0] > lon_vals[-1]:  # descending
        lon_slice = slice(west, east)
    else:                           # ascending
        lon_slice = slice(west, east)

    
    # Apply subset
    
    return ds.sel(latitude=lat_slice, longitude=lon_slice)
