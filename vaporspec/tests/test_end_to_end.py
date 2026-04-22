import vaporspec as vs
import xarray as xr
import os

def test_end_to_end():
    cu = vs.load_cu_atoc("data/cu_atoc_sept2020/cu_atoc_sept2020.csv")
    assert len(cu) > 0

    era = vs.load_era5(
        pressure_file="data/ERA5_sept2020/era5_pressure_humidity_temperature_sept2020.nc",
        singlelevel_file="data/ERA5_sept2020/era5_singlelevel_cloud_sp_sept2020.nc",
        radiation_file="data/ERA5_sept2020/era5_singlelevel_radiation_accum_sept2020.nc",
        subset_to_boulder=True
    )

    merged = vs.merge_cu_era5(cu, era)
    assert len(merged) > 0

    merged = vs.compute_surface_specific_humidity(merged)
    clear = vs.filter_clear_sky(merged)
    assert len(clear) > 0

    reg = vs.lw_down_vs_q850(clear)
    assert "slope" in reg

    era_map = xr.open_dataset("data/ERA5_sept2020/era5_LW_NA_1deg_sept2020.nc")
    lon, lat, LW, lon_min, lon_max, lat_min, lat_max = vs.prepare_lw_down_map(era_map)

    fig_scatter = vs.scatter_lw_vs_q850(clear)
    fig1 = vs.map_lw_down(lon, lat, LW, lon_min, lon_max, lat_min, lat_max)
    fig2 = vs.map_lw_down_zoom(lon, lat, LW, lon_min, lon_max, lat_min, lat_max)

    assert fig1 is not None
    assert fig2 is not None

    os.makedirs("tests/output", exist_ok=True)

    fig_scatter.savefig("tests/output/scatter_lw_q850.png", dpi=150)
    fig1.savefig("tests/output/map_north_america.png", dpi=150)
    fig2.savefig("tests/output/map_colorado_zoom.png", dpi=150)


    print("\n=== Statistical Summary ===")

    print(f"Total hours: {len(merged)}")
    print(f"Clear-sky hours: {len(clear)}")

    cloud_stats = vs.cloud_mask_stats(merged)
    print(f"Cloud stats: {cloud_stats}")

    print("LW↓ vs q850 regression:")
    print(f"  slope     = {reg['slope']:.3e}")
    print(f"  intercept = {reg['intercept']:.3e}")
    print(f"  r²        = {reg['r2']:.3f}")

    hb = vs.humidity_binned_comparison(merged)
    print("Humidity-binned comparison (10–12°C):")
    print(f"  Low-q mean  = {hb['low_mean']:.3e}")
    print(f"  High-q mean = {hb['high_mean']:.3e}")


    with open("tests/output/statistics.txt", "w") as f:
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
