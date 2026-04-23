# analysis.py
"""
Atmospheric diagnostics and statistical tools for vaporspec.

This module provides small, focused analysis functions used throughout
the project, including:
- simple linear regression tools
- LW↓ and LW↑ relationships with humidity and temperature
- humidity‑binned comparisons
- cloud‑mask statistics
- correlation matrices
- monthly and diurnal averages
- anomalies and smoothing
"""

import numpy as np
from sklearn.linear_model import LinearRegression   # simple linear regression model
from sklearn.preprocessing import StandardScaler    # optional feature standardization



# Regression tools

def regression_xy(x, y):
    """Run a simple linear regression of y on x."""
    x = np.array(x).reshape(-1, 1)                  # reshape for sklearn
    y = np.array(y)

    model = LinearRegression().fit(x, y)            # fit regression model
    r2 = model.score(x, y)                          # coefficient of determination

    return {
        "slope": model.coef_[0],
        "intercept": model.intercept_,
        "r2": r2,
        "model": model
    }


def regression_multi(X, y, standardize=True):
    """Run a multivariate linear regression."""
    X = np.array(X)
    y = np.array(y)

    if standardize:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)                 # standardize predictors

    model = LinearRegression().fit(X, y)            # fit regression model
    r2 = model.score(X, y)

    return {
        "coefficients": model.coef_,
        "intercept": model.intercept_,
        "r2": r2,
        "model": model
    }



# Confidence interval helper

def mean_ci(values, confidence=0.95):
    """Compute mean and confidence interval."""
    arr = np.array(values.dropna())                 # remove NaNs
    n = len(arr)
    mean = arr.mean()
    se = arr.std(ddof=1) / np.sqrt(n)               # standard error
    z = 1.96                                         # 95% CI
    return mean, mean - z * se, mean + z * se



# Domain‑specific diagnostics

def lw_down_vs_humidity(df):
    """LW↓ vs surface specific humidity."""
    return regression_xy(df["q_surface"], df["strd"])


def lw_down_vs_q850(df):
    """LW↓ vs 850 hPa specific humidity."""
    return regression_xy(df["q850"], df["strd"])


def lw_up_vs_temperature(df):
    """LW↑ vs surface temperature."""
    lw_up = df["strd"] - df["str"]                  # upward LW = down − net
    return regression_xy(df["Temp_Out_C"], lw_up)


def net_lw_vs_humidity(df):
    """Net LW vs surface specific humidity."""
    return regression_xy(df["q_surface"], df["str"])


def humidity_binned_comparison(df, tmin=10, tmax=12):
    """Compare net LW for low vs high humidity within a temperature range."""
    subset = df[(df["Temp_Out_C"] > tmin) & (df["Temp_Out_C"] < tmax)]  # temperature filter

    low_q = subset[subset["q_surface"] < subset["q_surface"].quantile(0.25)]   # lowest 25%
    high_q = subset[subset["q_surface"] > subset["q_surface"].quantile(0.75)]  # highest 25%

    low_mean, low_ci_low, low_ci_high = mean_ci(low_q["str"])
    high_mean, high_ci_low, high_ci_high = mean_ci(high_q["str"])

    return {
        "low_mean": low_mean,
        "low_ci": (low_ci_low, low_ci_high),
        "high_mean": high_mean,
        "high_ci": (high_ci_low, high_ci_high),
    }



# Correlation matrix

def correlation_matrix(df):
    """Compute correlation matrix for numeric columns."""
    return df.corr()



# Monthly means

def monthly_mean(df, time_col="time"):
    """Compute monthly mean values."""
    df = df.copy()
    df["month"] = df[time_col].dt.to_period("M")     # convert to monthly period
    return df.groupby("month").mean(numeric_only=True)



# Diurnal cycle

def diurnal_cycle(df, time_col="time"):
    """Compute hourly mean values."""
    df = df.copy()
    df["hour"] = df[time_col].dt.hour               # extract hour of day
    return df.groupby("hour").mean(numeric_only=True)



# Anomalies

def anomalies(df, time_col="time"):
    """Compute anomalies by removing monthly mean."""
    df = df.copy()
    df["month"] = df[time_col].dt.to_period("M")
    monthly = df.groupby("month").transform("mean")   # monthly climatology
    return df - monthly                               # anomaly = value − mean



# Rolling smoothing

def smooth(df, window=24):
    """Apply rolling mean smoothing."""
    return df.rolling(window=window, center=True).mean()



# Cloud‑mask diagnostics

def cloud_mask_stats(df, tcc_col="tcc"):
    """Compute simple cloud‑cover statistics."""
    return {
        "mean_tcc": df[tcc_col].mean(),
        "clear_fraction": (df[tcc_col] < 0.1).mean(),   # mostly clear
        "cloudy_fraction": (df[tcc_col] > 0.5).mean()   # mostly cloudy
    }
