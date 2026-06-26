
# Change Log

Space for documenting major updates to the `medsrtqc` package and their implications. 

## June 2026 - CHLA Reprocessing

### CHLA Processing Update

There are changes to the `CHLA` adjustment process that will change the value of `CHLA_ADJUSTED` and `CHLA_ADJUSTED_QC`, but should not require any change to other components of the processing chain except for the `SCIENTIFIC_CALIB` fields (below). 

The update to the dark count methodology does require the addition of the `CHLA_FLUORESCENCE_ADJUSTED` field (and corresponding `SCIENTIFIC_CALIB` values). It is under the name `FLU2` in the VMS infrastructure for now. 

### Resource File Handling

I have made changes to `resource_path()` that will hopefully minimize the amount of hard coded paths required. Basically, if the code is being run locally (i.e. is on the `C:\\` drive), it looks for resources like 'doxy_calib_coefficient.csv' internally. If it is on the server (`d:\\` or `e:\\` drive) it looks for those resources in the appropriate "MEDS" directory. These locations are still hardcoded in a `dict()` object in `medsrtqc.resources` '\_\_init\_\_.py'. 

For the functional directory they are all stored in 'Argo_QC/config/'. 

### SCIENTIFIC_CALIB Fields

The `SCIENTIFIC_CALIB_COMMENT` and `SCIENTIFIC_CALIB_EQUATION` fields for `CHLA` do not change based on the RTQC procedure, and therefore are not stored anywhere as they are the same every time (via "BGC-Argo quality control manual for the Chlorophyll-A concentration" v3.1):

- `SCIENTIFIC_CALIB_COMMENT`: CHLA real time adjustment (specified in http://dx.doi.org/10.13155/35385 and computed with MLD_LIMIT = 0.03, and following recommendations of Sauzede et al., 2025 (https://doi.org/10.17882/105732))
- `SCIENTIFIC_CALIB_EQUATION`: CHLA_ADJUSTED = CHLA_NPQ for PRES in [0, ZMaxFluo ], CHLA_ADJUSTED = ((FLUORESCENCE_CHLA-MEDIAN(PRELIM_DARK_CHLA))*SCALE_CHLA)/PHYSIO_RATIO

`CHLA_FLUORESCENCE` also has consistent `SCIENTIFIC_CALIB` fields:

- `SCIENTIFIC_CALIB_COMMENT`: CHLA_FLUORESCENCE real time adjustment (specified in http://dx.doi.org/10.13155/35385 and computed with MLD_LIMIT = 0.03)
- `SCIENTIFIC_CALIB_EQUATION`: CHLA_FLUORESCENCE_ADJUSTED = FLUORESCENCE_CHLA - MEDIAN(PRELIM_DARK_CHLA)

The `SCIENTIFIC_CALIB_COEFFICIENT` field will change every profile depending on the dark values and geographically determined physiological ratio of that profile. They are store both in the file 'Argo_QC/config/CHLA_netCDF_info.csv' and in the `SURF_CODE` under the name `CHLA_COEF` or `FLUO_COEF` for `FLU3` (`CHLA`) and `FLU2` (`FLUORESCENCE_CHLA`) respectively. 

An example:

- `SCIENTIFIC_CALIB_COEFFICIENT`: "PRELIM_DARK_CHLA=[55, 54, 55], SCALE_CHLA=0.0072, PHYSIO_RATIO=0.9502"

### Questions

- In a PROVOR CTS5 file I found positive longitudes that should be positive I believe. For now I have made a rule to flip any positive longitudes which is ok for now since we do not have any BGC floats in positive longitude regions, but this is not a permanent solution. How to proceed?