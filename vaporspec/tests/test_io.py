import vaporspec as vs
import pandas as pd
import xarray as xr

def test_load_cu_atoc():
    df = vs.load_cu_atoc("data/cu_atoc_sept2020/cu_atoc_sept2020.csv")
    assert isinstance(df, pd.DataFrame)
    assert "time" in df.columns
    assert len(df) > 0

def test_load_era5():
    era = vs.load_era5(
        pressure_file="data/ERA5_sept2020/era5_pressure_humidity_temperature_sept2020.nc",
        cloud_file="data/ERA5_sept2020/era5_singlelevel_cloud_sp_sept2020.nc",
        radiation_file="data/ERA5_sept2020/era5_singlelevel_radiation_accum_sept2020.nc",
        subset_to_boulder=True
    )
    assert isinstance(era, xr.Dataset)
    for var in ["q850", "t850", "sp", "tcc", "strd", "str"]:
        assert var in era
