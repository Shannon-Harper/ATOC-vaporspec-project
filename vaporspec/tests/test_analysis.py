import vaporspec as vs

def test_regression_outputs():
    import pandas as pd
    df = pd.DataFrame({
        "q_surface": [0.001, 0.002, 0.003],
        "strd": [300, 320, 350],
        "Temp_Out_C": [10, 12, 14],
        "str": [-300000, -310000, -320000],
        "q850": [0.001, 0.002, 0.003]
    })

    out = vs.lw_down_vs_q850(df)
    assert "slope" in out
    assert "intercept" in out
    assert "r2" in out

def test_cloud_mask_stats():
    import pandas as pd
    df = pd.DataFrame({"tcc": [0.0, 0.2, 0.8]})
    stats = vs.cloud_mask_stats(df)
    assert stats["mean_tcc"] > 0
    assert stats["clear_fraction"] > 0
