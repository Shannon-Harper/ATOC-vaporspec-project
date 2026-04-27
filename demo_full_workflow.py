# python demo_full_workflow.py

"""
Full end-to-end workflow for the vaporspec package.
This script is intended for manual execution (not pytest).

It performs:
1. Data loading (CU ATOC + ERA5)
2. Merging + clear-sky filtering
3. Diagnostics + regression
4. Scatter plots
5. Full-domain LW↓ map
6. Colorado zoom map
7. Saving figures + statistics summary
"""

import os
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import vaporspec as vs


# ============================================================
# Load CU ATOC station data
# ============================================================

cu = vs.load_cu_atoc("data/cu_atoc_sept2020/cu_atoc_sept2020.csv")
print(f"Loaded CU ATOC rows: {len(cu)}")


# ============================================================
# Load Boulder-subset ERA5 for regression
# ============================================================

era = vs.load_era5(
    pressure_file="data/ERA5_sept2020/era5_pressure_humidity_temperature_sept2020.nc",
    cloud_file="data/ERA5_sept2020/era5_singlelevel_cloud_sp_sept2020.nc",
    radiation_file="data/ERA5_sept2020/era5_singlelevel_radiation_accum_sept2020.nc",
    subset_to_boulder=True
)

print("Loaded Boulder ERA5 subset.")


# ============================================================
# Merge CU + ERA5 and compute clear-sky subset
# ============================================================

merged = vs.merge_cu_era5(cu, era)
print(f"Merged rows: {len(merged)}")

merged = vs.compute_surface_specific_humidity(merged)
clear = vs.filter_clear_sky(merged)
print(f"Clear-sky rows: {len(clear)}")


# ============================================================
# Load full-domain ERA5 for mapping
# ============================================================

era_map = xr.open_dataset("data/ERA5_sept2020/era5_LW_NA_1deg_sept2020.nc")
lon, lat, LW, lon_min, lon_max, lat_min, lat_max = vs.prepare_lw_down_map(era_map)

print(f"Map grid shape: {LW.shape}")


# ============================================================
# Full North America LW↓ map
# ============================================================

fig_map = vs.map_lw_down(lon, lat, LW, lon_min, lon_max, lat_min, lat_max)
plt.show()


# ============================================================
# Colorado zoom map
# ============================================================

fig_zoom = vs.map_lw_down_zoom(lon, lat, LW, lon_min, lon_max, lat_min, lat_max)
plt.show()


# ============================================================
# Scatter plots
# ============================================================

fig_qsurf = vs.scatter_lw_vs_q_surface(clear)
plt.show()

fig_fit = vs.scatter_lw_vs_q_surface_fit(clear)
plt.show()

fig_scatter_q850 = vs.scatter_lw_vs_q850(clear)
plt.show()

fig_lwup = vs.scatter_lw_up_vs_temp(clear)
plt.show()

fig_netlw = vs.scatter_net_lw_vs_q(clear)
plt.show()

fig_bins = vs.humidity_binned_barplot(clear)
plt.show()

# ============================================================
# Diagnostics + Regression
# ============================================================

print("\n=== Regression Diagnostics ===")

def print_reg(title, result):
    print(f"\n{title}")
    print(f"  slope     = {result['slope']:.3e}")
    print(f"  intercept = {result['intercept']:.3e}")
    print(f"  r²        = {result['r2']:.3f}")


# LW↓ vs q_surface
reg_qsurf = vs.lw_down_vs_humidity(clear)
print_reg("LW↓ vs q_surface", reg_qsurf)

# LW↓ vs q850
reg_q850 = vs.lw_down_vs_q850(clear)
print_reg("LW↓ vs q850", reg_q850)

# LW↑ vs Temp
reg_lwup = vs.lw_up_vs_temperature(clear)
print_reg("LW↑ vs Temp", reg_lwup)

# Net LW vs q_surface
reg_net = vs.net_lw_vs_humidity(clear)
print_reg("Net LW vs q_surface", reg_net)

print("\n=== Additional Physical + Statistical Tools ===")


# --- Core physics ---
print("\n--- Core Physics ---")

sample_T = 290.0  # K
sample_q = 0.008  # kg/kg
sample_RH = 0.45
sample_p = 90000  # Pa

print(f"Saturation vapor pressure at {sample_T} K: {vs.saturation_vapor_pressure(sample_T):.2f} Pa")
e = vs.vapor_pressure_from_rh(sample_T, sample_RH)
print(f"Vapor pressure from RH={sample_RH}: {e:.2f} Pa")
print(f"Mixing ratio: {vs.mixing_ratio(e, sample_p):.4e} kg/kg")
print(f"Specific humidity: {vs.specific_humidity(e, sample_p):.4e} kg/kg")
print(f"Clear-sky LW↓ (Brutsaert): {vs.clear_sky_lw_down(sample_T, sample_q):.2f} W/m²")
print(f"LW↑ from temperature: {vs.lw_up_from_temp(sample_T):.2f} W/m²")

# --- Regression tools ---
print("\n--- Regression Tools ---")

reg_simple = vs.regression_xy(clear["q_surface"], clear["strd"])
print(f"Simple regression r²: {reg_simple['r2']:.3f}")

X = np.column_stack([clear["q_surface"], clear["Temp_Out_C"]])
y = clear["strd"]
reg_multi = vs.regression_multi(X, y)
print(f"Multivariate regression r²: {reg_multi['r2']:.3f}")

# --- Correlation matrix ---
print("\n--- Correlation Matrix ---")
corr = vs.correlation_matrix(clear[["q_surface", "q850", "Temp_Out_C", "strd", "str"]])
print(corr)
# --- Cloud stats ---
print("\n--- Cloud Stats ---")
cloud_stats = vs.cloud_mask_stats(merged)
print(f"{cloud_stats}")

# --- Diurnal + monthly ---
print("\n--- Diurnal + Monthly ---")
diurnal = vs.diurnal_cycle(merged)
monthly = vs.monthly_mean(merged)
print("\nComputed diurnal and monthly means.")

# --- Humidity-binned comparison ---
print("\n--- Humidity-Binned Comparison (10–12°C) ---")
hb = vs.humidity_binned_comparison(merged)
print(f"low={hb['low_mean']:.3e}, high={hb['high_mean']:.3e}")

# --- Anomalies + smoothing ---
print("\n--- Anomalies + Smoothing ---")
anom = vs.anomalies(merged)
smooth_temp = vs.smooth(merged["Temp_Out_C"], window=24)
print("Computed anomalies and smoothed temperature series.")

# --- Confidence interval ---
print("\n--- Confidence Interval Example ---")
mean_val, ci_low, ci_high = vs.mean_ci(clear["strd"])
print(f"LW↓ mean={mean_val:.2f}, CI=({ci_low:.2f}, {ci_high:.2f})")

# ============================================================
# Save figures + statistics summary
# ============================================================

os.makedirs("figures", exist_ok=True)

fig_map.savefig("figures/map_north_america.png", dpi=150)
fig_zoom.savefig("figures/map_colorado_zoom.png", dpi=150)
fig_qsurf.savefig("figures/scatter_lw_q_surface.png", dpi=150)
fig_fit.savefig("figures/scatter_lw_q_surface_fit.png", dpi=150)
fig_scatter_q850.savefig("figures/scatter_lw_q850.png", dpi=150)
fig_lwup.savefig("figures/scatter_lw_up_temp.png", dpi=150)
fig_netlw.savefig("figures/scatter_net_lw_q.png", dpi=150)
fig_bins.savefig("figures/humidity_binned_barplot.png", dpi=150)

with open("figures/statistics.txt", "w") as f:
    f.write("=== Statistical Summary ===\n")
    f.write(f"Total hours: {len(merged)}\n")
    f.write(f"Clear-sky hours: {len(clear)}\n\n")

    f.write("LW↓ vs q850:\n")
    f.write(f"  slope     = {reg_q850['slope']:.3e}\n")
    f.write(f"  intercept = {reg_q850['intercept']:.3e}\n")
    f.write(f"  r²        = {reg_q850['r2']:.3f}\n\n")

    f.write("LW↓ vs q_surface:\n")
    f.write(f"  slope     = {reg_qsurf['slope']:.3e}\n")
    f.write(f"  intercept = {reg_qsurf['intercept']:.3e}\n")
    f.write(f"  r²        = {reg_qsurf['r2']:.3f}\n\n")

    f.write("LW↑ vs Temp:\n")
    f.write(f"  slope     = {reg_lwup['slope']:.3e}\n")
    f.write(f"  intercept = {reg_lwup['intercept']:.3e}\n")
    f.write(f"  r²        = {reg_lwup['r2']:.3f}\n\n")

    f.write("Net LW vs q_surface:\n")
    f.write(f"  slope     = {reg_net['slope']:.3e}\n")
    f.write(f"  intercept = {reg_net['intercept']:.3e}\n")
    f.write(f"  r²        = {reg_net['r2']:.3f}\n\n")

    f.write("Humidity-binned comparison (10–12°C):\n")
    f.write(f"  Low-q mean  = {hb['low_mean']:.3e}\n")
    f.write(f"  High-q mean = {hb['high_mean']:.3e}\n")

print("\nAll tests completed successfully.")
print("Figures and Statistics saved to ./figures/")
