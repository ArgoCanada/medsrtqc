
import numpy as np
import gsw


def betasw(P, T, S, lon, lat, wavelength, theta):
    # this function converted from matlab code for Zhang et al. (2009)

    # constants
    Na = 6.0221417930e23 # Avogadro's constant
    Kbz = 1.3806503e-23  # Boltzmann constant
    Tk = T + 273.15      # Absolute tempearture
    M0 = 18e-3           # Molecular weigth of water in kg/mol
    delta = 0.039        # depolarization ratio, Farinato and Roswell (1976)

    rad = theta*np.pi/180 # angle in radians

    # nsw: absolute refractive index of seawater
    # dnds: partial derivative of seawater refractive index w.r.t. salinity
    nsw, dnds = RInw(wavelength, T, S)

    # isothermal compressibility is from Lepple & Millero (1971,Deep
    # Sea-Research), pages 10-11
    # The error ~ +/-0.004e-6 bar^-1
    IsoComp = BetaT(T ,S)

    # density of seawater
    dens = gsw.rho_t_exact(gsw.SA_from_SP(S, P, lon, lat), T, P)

    # water activity data of seawater 
    dlnawds = dlnasw_ds(T, S)

    # density derivative of refractive index from PMH model
    dRI = PMH(nsw) # PMH model

    # volume scattering at 90 degree due to the density fluctuation
    beta_df = np.pi*np.pi/2*((wavelength*1e-9)**(-4))*Kbz*Tk*IsoComp*dRI**2*(6+6*delta)/(6-7*delta)
    # volume scattering at 90 degree due to the concentration fluctuation
    flu_con = S*M0*dnds**2/dens/(-dlnawds)/Na
    beta_cf = 2*np.pi*np.pi*((wavelength*1e-9)**(-4))*nsw**2*(flu_con)*(6+6*delta)/(6-7*delta)
    # total volume scattering at 90 degree
    beta90sw = beta_df+beta_cf

    beta_seawater = beta90sw*(1+((np.cos(rad))**2)*(1-delta)/(1+delta))

    return beta_seawater

def RInw(T, S, wavelength):
    # refractive index of air is from Ciddor (1996, Applied Optics)
    n_air = 1.0+(5792105.0/(238.0185-1/(wavelength/1e3)**2)+167917.0/(57.362-1/(wavelength/1e3)**2))/1e8
    # refractive index of seawater is from Quan and Fry (1994, Applied Optics)
    n = [
        1.31405, 1.779e-4, -1.05e-6, 1.6e-8,
        -2.02e-6, 15.868, 0.01155, -0.00423,
        -4382, 1.1455e6
    ]
    n_sw = n[0]+(n[1]+n[2]*T+n[3]*T**2)*S+n[4]*T**2+(n[5]+n[6]*S+n[7]*T)/wavelength+n[8]/wavelength**2+n[9]/wavelength**3 # pure seawater
    n_sw = n_sw*n_air

    dnsw_ds = (n[1]+n[2]*T+n[3]*T**2+n[6]/wavelength)*n_air

    return [n_sw, dnsw_ds]

def BetaT(T, S):

    # pure water secant bulk Millero (1980, Deep-sea Research)
    kw = 19652.21+148.4206*T-2.327105*T**2+1.360477e-2*T**3-5.155288e-5*T**4
    Btw_cal = 1/kw

    # seawater secant bulk
    a0 = 54.6746-0.603459*T+1.09987e-2*T**2-6.167e-5*T**3
    b0 = 7.944e-2+1.6483e-2*T-5.3009e-4*T**2

    Ks = kw + a0*S + b0*S**1.5

    # calculate seawater isothermal compressibility from the secant bulk
    IsoComp = 1/Ks*1e-5 # unit is pa

    return IsoComp


def dlnasw_ds(T, S):
    # water activity data of seawater is from Millero and Leung (1976,American
    # Journal of Science,276,1035-1077). Table 19 was reproduced using
    # Eqs.(14,22,23,88,107) then were fitted to polynominal equation.
    # dlnawds is partial derivative of natural logarithm of water activity
    # w.r.t. salinity

    dlnawds = (-5.58651e-4+2.40452e-7*T-3.12165e-9*T**2+2.40808e-11*T**3)+\
        1.5*(1.79613e-5-9.9422e-8*T+2.08919e-9*T**2-1.39872e-11*T**3)*S**0.5+\
        2*(-2.31065e-6-1.37674e-9*T-1.93316e-11*T**2)*S
    
    return dlnawds

def PMH(n_sw):
    # density derivative of refractive index from PMH model
    n_sw2 = n_sw**2
    n_density_derivative=(n_sw2-1)*(1+2/3*(n_sw2+2)*(n_sw/3-1/3/n_sw)**2)

    return n_density_derivative