# plotting.py
"""
Plotting utilities for vaporspec.

This module provides scatterplots and map visualizations used to explore
relationships between humidity and infrared radiation, including:
- LW↓ vs humidity scatterplots
- full North America LW↓ maps
- Colorado zoom maps
- ERA5 grid cell overlays
- humidity‑binned barplots
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs                       # map projections
import cartopy.feature as cfeature               # coastlines, borders, states
import seaborn as sns                            # regression plots

from .utils import set_plot_style                # shared plot styling



# Full North America LW↓ map

def map_lw_down(lon, lat, LW, lon_min, lon_max, lat_min, lat_max,
                title="ERA5 LW↓ Radiation — North America (Sept 2020)"):
    """Plot a full North America map of LW↓ using ERA5 monthly mean."""
    set_plot_style()

    fig = plt.figure(figsize=(12, 7.5), constrained_layout=True)
    ax = plt.axes(projection=ccrs.PlateCarree())   # simple lat/lon projection

    ax.set_extent([-140, -60, 20, 60], crs=ccrs.PlateCarree())  # NA domain

    # Map features
    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.7)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale("50m"), linewidth=0.3)

    # Filled contours
    cs = ax.contourf(lon, lat, LW, levels=20, cmap="viridis",
                     transform=ccrs.PlateCarree())

    add_zoom_region_box(ax)                        # highlight Colorado region

    cbar = plt.colorbar(cs, orientation="horizontal", pad=0.02, shrink=0.8)
    cbar.set_label("LW↓ Radiation (W/m²)")

    ax.set_title(title)
    return fig



# Colorado zoom map

def map_lw_down_zoom(lon, lat, LW, lon_min, lon_max, lat_min, lat_max,
                     title="ERA5 LW↓ Radiation — Colorado Zoom (Sept 2020)"):
    """Zoomed map over Colorado region."""
    set_plot_style()

    fig = plt.figure(figsize=(10, 7), constrained_layout=True)
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_extent([-110, -100, 36, 42], crs=ccrs.PlateCarree())  # Colorado box

    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.7)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"), linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale("50m"), linewidth=0.4)

    cs = ax.contourf(lon, lat, LW, levels=20, cmap="viridis",
                     transform=ccrs.PlateCarree())

    add_era5_grid_cell(ax, lon_min, lon_max, lat_min, lat_max)   # ERA5 grid cell
    add_boulder_marker(ax)                                       # CU ATOC marker

    cbar = plt.colorbar(cs, orientation="horizontal", pad=0.02, shrink=0.8)
    cbar.set_label("LW↓ Radiation (W/m²)")

    ax.set_title(title)
    return fig



# Helper: zoom region outline

def add_zoom_region_box(ax):
    """Draw the Colorado zoom region box."""
    zoom_lon_min, zoom_lon_max = -110, -100
    zoom_lat_min, zoom_lat_max = 36, 42

    ax.plot(
        [zoom_lon_min, zoom_lon_max, zoom_lon_max, zoom_lon_min, zoom_lon_min],
        [zoom_lat_min, zoom_lat_min, zoom_lat_max, zoom_lat_max, zoom_lat_min],
        color='cyan', linewidth=2, linestyle='--',
        transform=ccrs.PlateCarree(), label='Zoomed Area'
    )
    ax.legend(loc="lower left")



def add_boulder_marker(ax):
    """Add a marker for the CU ATOC station."""
    ax.plot(
        -105.27, 40.015,
        marker="o", markersize=6, color="red",
        transform=ccrs.PlateCarree(), label="CU ATOC station"
    )
    ax.legend(loc="lower left")



def add_era5_grid_cell(ax, lon_min, lon_max, lat_min, lat_max):
    """Draw the ERA5 analysis grid cell box."""
    ax.plot(
        [lon_min, lon_max, lon_max, lon_min, lon_min],
        [lat_min, lat_min, lat_max, lat_max, lat_min],
        color='cyan', linewidth=2, linestyle='--',
        transform=ccrs.PlateCarree(), label='ERA5 Analysis Grid Cell'
    )
    ax.legend(loc="lower left")



# Scatter plot: LW↓ vs surface specific humidity

def scatter_lw_vs_q_surface(df, title="Clear-Sky LW↓ vs Surface Specific Humidity (Boulder)"):
    """Scatter plot of LW↓ vs surface specific humidity."""
    set_plot_style()
    fig = plt.figure(figsize=(8, 6))
    plt.scatter(df["q_surface"], df["strd"], s=12, alpha=0.5, color="tab:blue")
    plt.xlabel("Surface Specific Humidity q (kg/kg)")
    plt.ylabel("Downwelling LW↓ Radiation (W/m²)")
    plt.title(title)
    plt.tight_layout()
    return fig



# Scatter plot: LW↑ vs surface temperature

def scatter_lw_up_vs_temp(df, title="Clear-Sky LW↑ vs Surface Temperature (Boulder)"):
    """Scatter plot of LW↑ vs surface temperature."""
    set_plot_style()
    lw_up = df["strd"] - df["str"]                  # upward LW = down − net
    fig = plt.figure(figsize=(8, 6))
    plt.scatter(df["Temp_Out_C"], lw_up, s=12, alpha=0.5, color="tab:orange")
    plt.xlabel("Surface Temperature (°C)")
    plt.ylabel("Upwelling LW↑ Radiation (W/m²)")
    plt.title(title)
    plt.tight_layout()
    return fig



# Scatter plot: Net LW vs surface specific humidity

def scatter_net_lw_vs_q(df, title="Clear-Sky Net LW vs Surface Specific Humidity (Boulder)"):
    """Scatter plot of net LW vs surface specific humidity."""
    set_plot_style()
    fig = plt.figure(figsize=(8, 6))
    plt.scatter(df["q_surface"], df["str"], s=12, alpha=0.5, color="tab:purple")
    plt.xlabel("Surface Specific Humidity q (kg/kg)")
    plt.ylabel("Net LW (W/m²)")
    plt.title(title)
    plt.tight_layout()
    return fig



# Scatter plot: LW↓ vs q850

def scatter_lw_vs_q850(df, title="Clear-Sky LW↓ vs 850 hPa Specific Humidity (Boulder)"):
    """Scatter plot of LW↓ vs q850 for clear-sky conditions."""
    set_plot_style()

    plt.figure(figsize=(8, 6))
    plt.scatter(df["q850"], df["strd"], s=10, alpha=0.5, color="tab:green")  # basic scatter

    plt.xlabel("850 hPa Specific Humidity q (kg/kg)")
    plt.ylabel("Downwelling LW↓ Radiation (W/m²)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()



# Scatter plot: LW↓ vs q_surface (linear fit)

def scatter_lw_vs_q_surface_fit(df, title="LW↓ vs q_surface (Linear Fit)"):
    """Scatter plot with linear regression fit."""
    set_plot_style()
    fig = plt.figure(figsize=(8, 6))
    sns.regplot(x=df["q_surface"], y=df["strd"],
                scatter_kws={"s": 12, "alpha": 0.4})
    plt.xlabel("Surface Specific Humidity q (kg/kg)")
    plt.ylabel("Downwelling LW↓ Radiation (W/m²)")
    plt.title(title)
    plt.tight_layout()
    return fig



# Bar plot: Net LW for low vs high humidity

def humidity_binned_barplot(df, tmin=10, tmax=12):
    """Bar plot comparing net LW for low vs high humidity."""
    set_plot_style()
    subset = df[(df["Temp_Out_C"] > tmin) & (df["Temp_Out_C"] < tmax)]  # temperature filter

    low_q = subset[subset["q_surface"] < subset["q_surface"].quantile(0.25)]
    high_q = subset[subset["q_surface"] > subset["q_surface"].quantile(0.75)]

    from .core import mean_ci
    low_mean, low_ci_low, low_ci_high = mean_ci(low_q["str"])
    high_mean, high_ci_low, high_ci_high = mean_ci(high_q["str"])

    means = [low_mean, high_mean]
    ci_lower = [low_mean - low_ci_low, high_mean - high_ci_low]
    ci_upper = [low_ci_high - low_mean, high_ci_high - high_mean]

    fig = plt.figure(figsize=(8, 6))
    plt.bar(["Low Humidity", "High Humidity"], means,
            yerr=[ci_lower, ci_upper], capsize=8,
            color=["skyblue", "salmon"])
    plt.ylabel("Net LW Radiation (W/m²)")
    plt.title(f"Net LW Radiation for Low vs High Humidity ({tmin}–{tmax}°C)")
    plt.tight_layout()
    return fig
