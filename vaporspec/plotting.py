# plotting.py
"""
Plotting utilities for vaporspec.
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import seaborn as sns

from .utils import set_plot_style
from .analysis import humidity_binned_comparison


def map_lw_down(lon, lat, LW, lon_min, lon_max, lat_min, lat_max,
                title="ERA5 LW↓ Radiation — North America (Sept 2020)"):
    set_plot_style()
    fig = plt.figure(figsize=(12, 7.5), constrained_layout=True)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-140, -60, 20, 60], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.7)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale("50m"), linewidth=0.3)

    cs = ax.contourf(lon, lat, LW, levels=20, cmap="viridis",
                     transform=ccrs.PlateCarree())

    cbar = plt.colorbar(cs, orientation="horizontal", pad=0.02, shrink=0.8)
    cbar.set_label("LW↓ Radiation (W/m²)")

    ax.set_title(title)
    return fig


def map_lw_down_zoom(lon, lat, LW, lon_min, lon_max, lat_min, lat_max,
                    title="ERA5 LW↓ Radiation — Colorado Zoom (Sept 2020)"):
    set_plot_style()
    fig = plt.figure(figsize=(10, 7), constrained_layout=True)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-110, -100, 36, 42], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.7)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale("50m"), linewidth=0.4)

    cs = ax.contourf(lon, lat, LW, levels=20, cmap="viridis",
                     transform=ccrs.PlateCarree())

    cbar = plt.colorbar(cs, orientation="horizontal", pad=0.02, shrink=0.8)
    cbar.set_label("LW↓ Radiation (W/m²)")

    ax.set_title(title)
    return fig


def scatter_lw_vs_q_surface(df):
    set_plot_style()
    fig = plt.figure(figsize=(8, 6))
    plt.scatter(df["q_surface"], df["strd"], s=12, alpha=0.5)
    plt.xlabel("Surface Specific Humidity")
    plt.ylabel("LW↓ Radiation")
    plt.tight_layout()
    return fig


def humidity_binned_barplot(df, tmin=10, tmax=12):
    set_plot_style()
    stats = humidity_binned_comparison(df, tmin=tmin, tmax=tmax)

    fig = plt.figure(figsize=(8, 6))
    plt.bar(["Low", "High"],
            [stats["low_mean"], stats["high_mean"]])
    plt.ylabel("Net LW Radiation")
    plt.tight_layout()
    return fig


# ============================================================
# YOUR CONTRIBUTION
# ============================================================

def plot_diurnal_cycle(df, variable="strd"):
    """
    Plot the diurnal cycle (hourly mean) of a selected variable.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset containing a datetime index or a 'time' column.
    variable : str, default "strd"
        Column name of the variable to plot.

    Returns
    -------
    matplotlib.figure.Figure
    """
    import pandas as pd

    # handle time column or index
    if "time" in df.columns:
        time = pd.to_datetime(df["time"])
    else:
        time = pd.to_datetime(df.index)

    data = df.copy()
    data["hour"] = time.dt.hour

    # compute hourly mean
    hourly_mean = data.groupby("hour")[variable].mean()

    # plot
    fig = plt.figure(figsize=(10, 6))
    plt.plot(hourly_mean.index, hourly_mean.values, marker="o")

    plt.xlabel("Hour of Day")
    plt.ylabel(variable)
    plt.title(f"Diurnal Cycle of {variable}")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig
