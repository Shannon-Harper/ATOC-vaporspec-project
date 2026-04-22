# vaporspec

**vaporspec** is a Python toolkit for analyzing atmospheric water vapor and infrared radiation using real observational datasets.  
It is built around a focused case study: **September 2020** in **Boulder, Colorado**, combining CU ATOC surface observations with ERA5 reanalysis fields.

The package provides tools for loading datasets, computing humidity–IR relationships, performing simple radiative diagnostics, and generating publication‑quality visualizations — including scatter plots, binned comparisons, and two‑stage mapping workflows.

---

## Features

### **Data I/O**
- Load CU ATOC weather station data (IR fluxes, humidity, temperature)  
- Load ERA5 reanalysis humidity and radiation fields  
- Merge surface observations with ERA5 profiles  
- Compute surface specific humidity  
- Filter clear‑sky conditions  
- Extract ERA5 grid cell boundaries for mapping  

### **Core Physics**
- Beer–Lambert absorption  
- Broadband LW transmittance approximation  
- Saturation vapor pressure (Tetens)  
- Specific humidity and mixing ratio  
- Clear‑sky LW↓ (Brutsaert)  
- Stefan–Boltzmann LW↑  

### **Atmospheric Diagnostics**
- LW↓ vs humidity  
- LW↑ vs surface temperature  
- Net LW vs humidity  
- Humidity‑binned comparisons  
- Regression tools  
- Cloud‑mask statistics  
- Diurnal and monthly means  

### **Visualization**
- Scatterplots with regression fits  
- Humidity‑binned bar plots  
- North America LW↓ maps  
- Colorado zoom maps with:
  - ERA5 analysis grid cell  
  - CU ATOC station marker  
  - Zoom‑region outline  

---

## Installation

### **From source**
```bash
git clone https://github.com/Shannon-Harper/ATOC-vaporspec-project.git
cd vaporspec
pip install -e .
# ATOC-vaporspec-project
