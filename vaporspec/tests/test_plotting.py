import vaporspec as vs
import matplotlib.figure as mf
import pandas as pd
import numpy as np

def test_scatter_plot():
    df = pd.DataFrame({
        "q850": np.random.rand(10),
        "strd": np.random.rand(10) * 100,
    })
    fig = vs.scatter_lw_vs_q850(df)
    assert isinstance(fig, mf.Figure)

def test_map_functions():
    lon = np.linspace(-110, -100, 10)
    lat = np.linspace(36, 42, 10)
    LW = np.random.rand(10, 10)
    fig = vs.map_lw_down(lon, lat, LW, -105.5, -104.5, 39.5, 40.5)
    assert isinstance(fig, mf.Figure)
