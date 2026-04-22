"""
test_vaporspec.py

Full end-to-end workflow for the vaporspec package.
This script is intended for manual execution (not pytest).

It performs:
1. Data loading (CU ATOC + ERA5)
2. Merging + clear-sky filtering
3. Diagnostics + regression
4. Scatter plot
5. Full-domain LW↓ map
6. Colorado zoom map
7. Saving figures + statistics summary
"""

import os
import xarray as xr
import matplotlib.pyplot as plt
import vaporspec as vs


# ============================================================
# 1. Load CU ATOC station data
# ============================================================

cu = vs.load_cu_atoc("data/cu_atoc_sept2020/cu_atoc_sept2020.csv")
print(f"Loaded CU ATOC rows: {len(cu)}")


# ============================================================
# 2. Load Boulder-subset ERA5 for regression
# ============================================================

era = vs.load_era5(
    pressure_file="data/ERA5_sept2020/era5_pressure_humidity_temperature_sept2020.nc",
    singlelevel_file="data/ERA5_sept2020/era5_singlelevel_cloud_sp_sept2020.nc",
    radiation_file="data/ERA5_sept2020/era5_singlelevel_radiation_accum_sept2020.nc",
    subset_to_boulder=True
)

print("Loaded Boulder ERA5 subset.")


# ============================================================
# 3. Merge CU + ERA5 and compute clear-sky subset
# ============================================================

merged = vs.merge_cu_era5(cu, era)
print(f"Merged rows: {len(merged)}")

merged = vs.compute_surface_specific_humidity(merged)
clear = vs.filter_clear_sky(merged)
print(f"Clear-sky rows: {len(clear)}")


# ============================================================
# 4. Diagnostics + Regression
# ============================================================

print("\n=== Diagnostics ===")

reg = vs.lw_down_vs_q850(clear)
print(f"LW↓ vs q850: slope={reg['slope']:.3e}, intercept={reg['intercept']:.3e}, r²={reg['r2']:.3f}")

cloud_stats = vs.cloud_mask_stats(merged)
print(f"Cloud stats: {cloud_stats}")

diurnal = vs.diurnal_cycle(merged)
print("Computed diurnal cycle.")

monthly = vs.monthly_mean(merged)
print("Computed monthly means.")

hb = vs.humidity_binned_comparison(merged)
print(f"Humidity-binned comparison (10–12°C): low={hb['low_mean']:.3e}, high={hb['high_mean']:.3e}")


# ============================================================
# 5. Scatter plot: LW↓ vs q850
# ============================================================

fig_scatter = vs.scatter_lw_vs_q850(clear)
plt.show()


# ============================================================
# 6. Load full-domain ERA5 for mapping
# ============================================================

era_map = xr.open_dataset("data/ERA5_sept2020/era5_LW_NA_1deg_sept2020.nc")
lon, lat, LW, lon_min, lon_max, lat_min, lat_max = vs.prepare_lw_down_map(era_map)

print(f"Map grid shape: {LW.shape}")


# ============================================================
# 7. Full North America LW↓ map
# ============================================================

fig_map = vs.map_lw_down(lon, lat, LW, lon_min, lon_max, lat_min, lat_max)
plt.show()


# ============================================================
# 8. Colorado zoom map
# ============================================================

fig_zoom = vs.map_lw_down_zoom(lon, lat, LW, lon_min, lon_max, lat_min, lat_max)
plt.show()


# ============================================================
# 9. Additional scatter plots (optional)
# ============================================================

fig_qsurf = vs.scatter_lw_vs_q_surface(clear)
plt.show()

fig_lwup = vs.scatter_lw_up_vs_temp(clear)
plt.show()

fig_netlw = vs.scatter_net_lw_vs_q(clear)
plt.show()

fig_fit = vs.scatter_lw_vs_q_surface_fit(clear)
plt.show()

fig_bins = vs.humidity_binned_barplot(clear)
plt.show()


# ============================================================
# 10. Save figures + statistics summary
# ============================================================

os.makedirs("figures", exist_ok=True)

fig_scatter.savefig("figures/scatter_lw_q850.png", dpi=150)
fig_map.savefig("figures/map_north_america.png", dpi=150)
fig_zoom.savefig("figures/map_colorado_zoom.png", dpi=150)
fig_qsurf.savefig("figures/scatter_lw_q_surface.png", dpi=150)
fig_lwup.savefig("figures/scatter_lw_up_temp.png", dpi=150)
fig_netlw.savefig("figures/scatter_net_lw_q.png", dpi=150)
fig_fit.savefig("figures/scatter_lw_q_surface_fit.png", dpi=150)
fig_bins.savefig("figures/humidity_binned_barplot.png", dpi=150)

with open("figures/statistics.txt", "w") as f:
    f.write("=== Statistical Summary ===\n")
    f.write(f"Total hours: {len(merged)}\n")
    f.write(f"Clear-sky hours: {len(clear)}\n")
    f.write(f"Cloud stats: {cloud_stats}\n")
    f.write("LW↓ vs q850 regression:\n")
    f.write(f"  slope     = {reg['slope']:.3e}\n")
    f.write(f"  intercept = {reg['intercept']:.3e}\n")
    f.write(f"  r²        = {reg['r2']:.3f}\n")
    f.write("Humidity-binned comparison (10–12°C):\n")
    f.write(f"  Low-q mean  = {hb['low_mean']:.3e}\n")
    f.write(f"  High-q mean = {hb['high_mean']:.3e}\n")

print("\nAll tests completed successfully.")
print("Figures saved to ./figures/")
