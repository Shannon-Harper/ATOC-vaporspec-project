# core.py
"""
Core physical and statistical functions for vaporspec.

Includes:
- Beer–Lambert absorption
- Broadband LW transmittance approximation
- Saturation vapor pressure (Tetens)
- Vapor pressure from RH
- Mixing ratio
- Specific humidity
- Clear-sky LW↓ (Brutsaert)
- Stefan–Boltzmann LW↑
- Linear regression
- Confidence intervals
"""

import numpy as np
from scipy.stats import t


# Beer–Lambert absorption

def beer_lambert(q, k, m):
    """
    Simple Beer–Lambert absorption model.

    Parameters
    ----------
    q : float or array
        Specific humidity (kg/kg)
    k : float
        Absorption coefficient
    m : float
        Mass path (kg/m²)

    Returns
    -------
    float or array
        Transmittance (0–1)
    """
    return np.exp(-k * q * m)


# Broadband LW transmittance approximation

def broadband_transmittance(q, T):
    """
    Approximate broadband LW transmittance as a function of
    specific humidity and temperature.

    This is a simplified placeholder model — not a full RRTM.

    Parameters
    ----------
    q : float or array
        Specific humidity (kg/kg)
    T : float or array
        Temperature (K)

    Returns
    -------
    float or array
        Broadband transmittance (0–1)
    """
    a = 120.0
    b = 0.1
    return np.exp(-a * q) * (T / 300.0) ** b


# Saturation vapor pressure (Tetens)

def saturation_vapor_pressure(T):
    """
    Saturation vapor pressure (Pa) using Tetens formula.
    T : temperature in Kelvin
    """
    Tc = T - 273.15
    return 610.94 * np.exp((17.625 * Tc) / (Tc + 243.04))


# Vapor pressure from RH

def vapor_pressure_from_rh(T, RH):
    """
    Vapor pressure (Pa) from temperature (K) and RH (0–1).
    """
    es = saturation_vapor_pressure(T)
    return RH * es


# Mixing ratio (kg/kg)

def mixing_ratio(e, p):
    """
    Mixing ratio (kg/kg)
    e : vapor pressure (Pa)
    p : total pressure (Pa)
    """
    epsilon = 0.622
    return epsilon * e / (p - e)


# Specific humidity (kg/kg)

def specific_humidity(e, p):
    """
    Specific humidity (kg/kg)
    """
    w = mixing_ratio(e, p)
    return w / (1 + w)


# Clear-sky LW↓ (Brutsaert 1975)

def clear_sky_lw_down(T, q):
    """
    Empirical clear-sky LW↓ model.
    T : surface temperature (K)
    q : specific humidity (kg/kg)
    Returns LW↓ in W/m².
    """
    emiss = 1.24 * (q * 1e3 / T)**(1/7)
    sigma = 5.67e-8
    return emiss * sigma * T**4


# Stefan–Boltzmann LW↑

def lw_up_from_temp(T):
    """
    LW↑ from surface temperature (K) using Stefan–Boltzmann law.
    """
    sigma = 5.67e-8
    return sigma * T**4


# Linear regression (original version)

def regression(x, y):
    """
    Simple linear regression: y = a*x + b

    Parameters
    ----------
    x, y : array-like

    Returns
    -------
    slope, intercept, r2
    """
    x = np.array(x)
    y = np.array(y)

    slope, intercept = np.polyfit(x, y, 1)
    y_pred = slope * x + intercept

    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot

    return slope, intercept, r2


# Confidence interval helper (original version)

def mean_ci(data, confidence=0.95):
    """
    Compute mean and confidence interval.

    Parameters
    ----------
    data : array-like
    confidence : float

    Returns
    -------
    mean, lower_bound, upper_bound
    """
    a = np.array(data)
    n = len(a)
    m = np.mean(a)
    se = np.std(a, ddof=1) / np.sqrt(n)
    h = se * t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h
