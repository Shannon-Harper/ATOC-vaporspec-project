"""
vaporspec: A Python toolkit for atmospheric water vapor and infrared analysis.

This package provides tools for:
- Loading IR radiometer, humidity, and meteorological datasets
- Performing physical calculations related to water vapor absorption
- Computing diagnostics linking humidity and infrared radiation
- Creating publication-quality visualizations

Modules
-------
io          : Data loading utilities for CU ATOC, ERA5, and radiometer files
core        : Physical calculations (Beer–Lambert, transmittance, humidity metrics)
analysis    : Atmospheric diagnostics and IR–humidity relationships
plotting    : Visualization tools for time series, scatterplots, and maps
utils       : Helper functions shared across modules
"""

# IO

from .io import (
    load_cu_atoc,
    load_era5,
    merge_cu_era5,
    compute_surface_specific_humidity,
    filter_clear_sky,
    prepare_lw_down_map,
)

# Core Physics

from .core import (
    beer_lambert,
    broadband_transmittance,
    saturation_vapor_pressure,
    vapor_pressure_from_rh,
    mixing_ratio,
    specific_humidity,
    clear_sky_lw_down,
    lw_up_from_temp,
    regression,
    mean_ci,
)

# Analysis Suite

from .analysis import (
    # Domain-specific diagnostics
    lw_down_vs_humidity,
    lw_down_vs_q850,
    lw_up_vs_temperature,
    net_lw_vs_humidity,
    humidity_binned_comparison,

    # General analysis tools
    regression_xy,
    regression_multi,
    correlation_matrix,
    monthly_mean,
    diurnal_cycle,
    anomalies,
    smooth,
    cloud_mask_stats,
)

# Plotting

from .plotting import (
    scatter_lw_vs_q850,
    map_lw_down,
    map_lw_down_zoom,
    add_boulder_marker,
    scatter_lw_vs_q_surface,
    scatter_lw_up_vs_temp,
    scatter_net_lw_vs_q,
    scatter_lw_vs_q_surface_fit,
    humidity_binned_barplot,
)

# Public API

__all__ = [
    # IO
    "load_cu_atoc",
    "load_era5",
    "merge_cu_era5",
    "compute_surface_specific_humidity",
    "filter_clear_sky",
    "prepare_lw_down_map",

    # Core physics
    "beer_lambert",
    "broadband_transmittance",
    "saturation_vapor_pressure",
    "vapor_pressure_from_rh",
    "mixing_ratio",
    "specific_humidity",
    "clear_sky_lw_down",
    "lw_up_from_temp",
    "regression",
    "mean_ci",

    # Analysis (domain-specific)
    "lw_down_vs_humidity",
    "lw_down_vs_q850",
    "lw_up_vs_temperature",
    "net_lw_vs_humidity",
    "humidity_binned_comparison",

    # Analysis (general)
    "regression_xy",
    "regression_multi",
    "correlation_matrix",
    "monthly_mean",
    "diurnal_cycle",
    "anomalies",
    "smooth",
    "cloud_mask_stats",

    # Plotting
    "scatter_lw_vs_q850",
    "map_lw_down",
    "map_lw_down_zoom",
    "add_boulder_marker",
    "scatter_lw_vs_q_surface",
    "scatter_lw_up_vs_temp",
    "scatter_net_lw_vs_q",
    "scatter_lw_vs_q_surface_fit",
    "humidity_binned_barplot",

]

__version__ = "0.1.0"
