# core.py
"""
Core physical and statistical functions for vaporspec.

This module contains small, self‑contained tools used throughout the
project, including:
- Beer–Lambert absorption
- Broadband LW transmittance approximation
- Saturation vapor pressure (Tetens)
- Vapor pressure from RH
- Mixing ratio and specific humidity
- Clear‑sky LW↓ (Brutsaert)
- Stefan–Boltzmann LW↑
- Simple linear regression
- Confidence intervals
"""

import numpy as np
from scipy.stats import t               # t‑distribution for confidence intervals



# Beer–Lambert absorption

def beer_lambert(q, k, m):
    """Simple Beer–Lambert absorption model."""
    return np.exp(-k * q * m)           # exponential attenuation



# Broadband LW transmittance approximation

def broadband_transmittance(q, T):
    """Approximate broadband LW transmittance.
    This is a placeholder model capturing:
    - exponential humidity dependence
    - weak temperature dependence"""
    a = 120.0
    b = 0.1
    return np.exp(-a * q) * (T / 300.0) ** b



# Saturation vapor pressure (Tetens)

def saturation_vapor_pressure(T):
    """Saturation vapor pressure (Pa) using Tetens formula."""
    Tc = T - 273.15                     # convert K → °C
    return 610.94 * np.exp((17.625 * Tc) / (Tc + 243.04))



# Vapor pressure from RH

def vapor_pressure_from_rh(T, RH):
    """Vapor pressure (Pa) from temperature (K) and RH (0–1)."""
    es = saturation_vapor_pressure(T)   # saturation vapor pressure
    return RH * es                      # actual vapor pressure



# Mixing ratio (kg/kg)

def mixing_ratio(e, p):
    """Compute mixing ratio (kg/kg)."""
    epsilon = 0.622
    return epsilon * e / (p - e)



# Specific humidity (kg/kg)

def specific_humidity(e, p):
    """Compute specific humidity (kg/kg)."""
    w = mixing_ratio(e, p)
    return w / (1 + w)                  # mixing ratio to specific humidity



# Clear-sky LW↓ (Brutsaert 1975)

def clear_sky_lw_down(T, q):
    """Empirical clear‑sky LW↓ model (Brutsaert 1975)."""
    emiss = 1.24 * (q * 1e3 / T)**(1/7) # empirical emissivity
    sigma = 5.67e-8                     # Stefan–Boltzmann constant
    return emiss * sigma * T**4         # LW↓ = emissivity * σT⁴



# Stefan–Boltzmann LW↑

def lw_up_from_temp(T):
    """LW↑ from surface temperature (K) using Stefan–Boltzmann law."""
    sigma = 5.67e-8
    return sigma * T**4                 # LW↑ = σT⁴



# Linear regression

def regression(x, y):
    """Simple linear regression: y = a*x + b."""
    x = np.array(x)                     # convert to numpy
    y = np.array(y)

    slope, intercept = np.polyfit(x, y, 1)   # best‑fit line
    y_pred = slope * x + intercept           # predicted values

    ss_res = np.sum((y - y_pred) ** 2)       # residual sum of squares
    ss_tot = np.sum((y - np.mean(y)) ** 2)   # total variance
    r2 = 1 - ss_res / ss_tot                 # coefficient of determination

    return slope, intercept, r2



# Confidence interval helper

def mean_ci(data, confidence=0.95):
    """Compute mean and confidence interval."""
    a = np.array(data)                 # convert to numpy
    n = len(a)

    if n < 2:
        m = float(a.mean()) if n == 1 else np.nan
        return m, m, m
    
    m = np.mean(a)                     # sample mean
    se = np.std(a, ddof=1) / np.sqrt(n)  # standard error
    h = se * t.ppf((1 + confidence) / 2., n - 1)  # margin of error
    return m, m - h, m + h
