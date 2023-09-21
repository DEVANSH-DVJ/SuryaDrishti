#####################################################
# @Author: Abhilash Sarwade
# @Date:   2022-10-31 13:21:07
# @email: sarwade@ursc.gov.in
# @File Name: xsm_gen_lc.py
# @Project: None

# @Last Modified time: 2023-01-23 11:10:26
#####################################################


import os

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt

"""
ene_lo = 1.551 #keV
ene_hi = 12.408 #keV
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

effarea = np.loadtxt(os.path.join(BASE_DIR, 'scripts', 'xsm_onaxis_effective_area.txt'))


def xsm_gen_lc(spec_file, ene_lo, ene_hi):
    hdu1 = fits.open(spec_file)
    hdu = fits.BinTableHDU.from_columns(hdu1[1].columns)

    data = hdu.data

    time_xsm = (data['TSTART'] + data['TSTOP']) / 2.
    tbinsize = (data['TSTOP'][0] - data['TSTART'][0])

    exposure = data['EXPOSURE']

    ns = len(data)
    fluxlc = np.zeros(ns)
    countlc = np.zeros(ns)
    count_err = np.zeros(ns)
    flux_err = np.zeros(ns)

    ene = np.arange(0, 512) * 0.033 + 0.5 + 0.033 / 2.0  # Midpoint energy of PI bins

    kev2erg = 1.6021e-9
    cgs2si = 0.001

    startch = int((ene_lo - 0.5) / 0.033)
    stopch = int((ene_hi - 0.5) / 0.033)

    for i in range(0, ns):
        spec = data['COUNTS'][i] / data['EXPOSURE'][i]
        spec_ene = spec * ene / effarea
        fluxlc[i] = np.sum(spec_ene[startch:stopch]) * kev2erg * cgs2si
        countlc[i] = np.sum(spec[startch:stopch])
        err = np.sqrt(data['STAT_ERR'][i]**2 + data['SYS_ERR'][i]**2) / data['EXPOSURE'][i]
        err_ene = err * ene / effarea
        count_err[i] = np.sum(err[startch:stopch])
        flux_err[i] = np.sum(err_ene[startch:stopch]) * kev2erg * cgs2si

    # Select only bins with atleast half exposure for tbinsize >=10
    if (tbinsize >= 10.0):
        ind = (exposure > max(exposure) / 2.0)
        time_xsm = time_xsm[ind]
        fluxlc = fluxlc[ind]
        countlc = countlc[ind]
        exposure = exposure[ind]
        count_err = count_err[ind]
        flux_err = flux_err[ind]

    nbins = int(86400.0 / tbinsize)

    tday0 = int(time_xsm[0] / 86400.0) * 86400.0
    t0 = (time_xsm[0] - int((time_xsm[0] - tday0) / tbinsize) * tbinsize)
    alltime = np.arange(0, nbins) * tbinsize + t0
    allflux = np.empty(nbins)
    allflux[:] = np.nan
    allflux_err = np.empty(nbins)
    allflux_err[:] = 0
    allcount = np.empty(nbins)
    allcount[:] = np.nan
    allcount_err = np.empty(nbins)
    allcount_err[:] = 0

    for i, t in enumerate(time_xsm):
        tbin = int((t - tday0) / tbinsize)
        allflux[tbin] = fluxlc[i]
        allflux_err[tbin] = flux_err[i]
        allcount[tbin] = countlc[i]
        allcount_err[tbin] = count_err[i]

    return alltime, allflux, allcount, allflux_err, allcount_err


def creat_lc_hdulist(alltime, allflux, allcount, allflux_err, allcount_err):

    hdu_list = []
    primary_hdu = fits.PrimaryHDU()

    hdu_list.append(primary_hdu)

    fits_columns = []
    col1 = fits.Column(name='TIME', format='D', unit='s', array=alltime)
    col3 = fits.Column(name='FLUX', format='D', unit='W/m^2', array=allflux)
    col2 = fits.Column(name='RATE', format='D', unit='count/s', array=allcount)
    col4 = fits.Column(name='ERROR', format='D', array=allflux_err)
    col5 = fits.Column(name='ERROR_CNT', format='D', array=allcount_err)
    fits_columns.append(col1)
    fits_columns.append(col2)
    fits_columns.append(col3)
    fits_columns.append(col4)
    fits_columns.append(col5)

    hdu_lc = fits.BinTableHDU.from_columns(fits.ColDefs(fits_columns))
    hdu_lc.name = 'RATE'

    hdu_list.append(hdu_lc)

    _hdu_list = fits.HDUList(hdus=hdu_list)
    # _hdu_list.writeto(f'{outfile}.lc')
    return _hdu_list


def write_lc_file(spec_file, ene_lo, ene_hi, outfile):
    alltime, allflux, allcount, allflux_err, allcount_err = xsm_gen_lc(spec_file, ene_lo, ene_hi)
    _hdu_list = creat_lc_hdulist(alltime, allflux, allcount, allflux_err, allcount_err)
    _hdu_list[1].header.set("START_E", f'{ene_lo:.4f} keV')
    _hdu_list[1].header.set("STOP_E", f'{ene_hi:.4f} keV')
    _hdu_list.writeto(outfile, overwrite=True)


if __name__ == '__main__':
    ene = np.arange(0, 512) * 0.033 + 0.5 + 0.033 / 2.0  # Midpoint energy of PI bins
    plt.plot(ene, effarea)
    plt.show()
