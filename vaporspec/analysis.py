# analysis.py
"""
Atmospheric diagnostics and statistical tools for vaporspec.

Includes:
- LW↓ vs surface specific humidity
- LW↓ vs 850 hPa specific humidity
- LW↑ vs surface temperature
- Net LW vs humidity
- Humidity-binned comparisons
- Regression tools
- Correlation matrix
- Monthly means
- Diurnal cycle
- Anomalies
- Rolling smoothing
- Cloud-mask diagnostics
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler




# Generic Regression Tools

def regression_xy(x, y):
    """Simple linear regression y = a*x + b."""
    x = np.array(x).reshape(-1, 1)
    y = np.array(y)

    model = LinearRegression().fit(x, y)
    r2 = model.score(x, y)

    return {
        "slope": model.coef_[0],
        "intercept": model.intercept_,
        "r2": r2,
        "model": model
    }


def regression_multi(X, y, standardize=True):
    """Multivariate regression."""
    X = np.array(X)
    y = np.array(y)

    if standardize:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

    model = LinearRegression().fit(X, y)
    r2 = model.score(X, y)

    return {
        "coefficients": model.coef_,
        "intercept": model.intercept_,
        "r2": r2,
        "model": model
    }



# Confidence Interval for Mean

def mean_ci(values, confidence=0.95):
    """Mean + confidence interval."""
    arr = np.array(values.dropna())
    n = len(arr)
    mean = arr.mean()
    se = arr.std(ddof=1) / np.sqrt(n)
    z = 1.96  # 95%
    return mean, mean - z * se, mean + z * se



# Domain-Specific Diagnostics

def lw_down_vs_humidity(df):
    """LW↓ vs surface specific humidity."""
    return regression_xy(df["q_surface"], df["strd"])


def lw_down_vs_q850(df):
    """LW↓ vs 850 hPa specific humidity."""
    return regression_xy(df["q850"], df["strd"])


def lw_up_vs_temperature(df):
    """LW↑ vs surface temperature."""
    lw_up = df["strd"] - df["str"]
    return regression_xy(df["Temp_Out_C"], lw_up)


def net_lw_vs_humidity(df):
    """Net LW vs surface specific humidity."""
    return regression_xy(df["q_surface"], df["str"])


def humidity_binned_comparison(df, tmin=10, tmax=12):
    """
    Compare net LW for low vs high humidity within a temperature subset.
    """
    subset = df[(df["Temp_Out_C"] > tmin) & (df["Temp_Out_C"] < tmax)]

    low_q = subset[subset["q_surface"] < subset["q_surface"].quantile(0.25)]
    high_q = subset[subset["q_surface"] > subset["q_surface"].quantile(0.75)]

    low_mean, low_ci_low, low_ci_high = mean_ci(low_q["str"])
    high_mean, high_ci_low, high_ci_high = mean_ci(high_q["str"])

    return {
        "low_mean": low_mean,
        "low_ci": (low_ci_low, low_ci_high),
        "high_mean": high_mean,
        "high_ci": (high_ci_low, high_ci_high),
    }



# Correlation Matrix

def correlation_matrix(df):
    """Compute correlation matrix."""
    return df.corr()


# Monthly Means

def monthly_mean(df, time_col="time"):
    """Compute monthly means."""
    df = df.copy()
    df["month"] = df[time_col].dt.to_period("M")
    return df.groupby("month").mean(numeric_only=True)


# Diurnal Cycle

def diurnal_cycle(df, time_col="time"):
    """Compute hourly means."""
    df = df.copy()
    df["hour"] = df[time_col].dt.hour
    return df.groupby("hour").mean(numeric_only=True)


# Anomalies

def anomalies(df, time_col="time"):
    """Compute anomalies by removing monthly mean."""
    df = df.copy()
    df["month"] = df[time_col].dt.to_period("M")
    monthly = df.groupby("month").transform("mean")
    return df - monthly


# Rolling Smoothing

def smooth(df, window=24):
    """Rolling mean smoothing."""
    return df.rolling(window=window, center=True).mean()



# Cloud-Mask Diagnostics

def cloud_mask_stats(df, tcc_col="tcc"):
    """Compute cloud cover statistics."""
    return {
        "mean_tcc": df[tcc_col].mean(),
        "clear_fraction": (df[tcc_col] < 0.1).mean(),
        "cloudy_fraction": (df[tcc_col] > 0.5).mean()
    }
