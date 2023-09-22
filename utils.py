"""
Import python libraries
"""
import os
from sys import exit  # For some reason standard `exit(0)` doesn't work
from datetime import date as dt
import datetime as dtt
from typing import Any, Tuple

"""
Import other libraries
"""
import numpy as np
import numpy.typing as npt
from astropy.convolution import convolve, Gaussian1DKernel
from astropy.io import fits
import netCDF4 as nc

"""
Function to verify correctness of config and iconfig file
Inputs:
    1. Config file
    2. IConfig file
Outputs:
    None. LC object creation exits with error if config or iconfig file
    is incorrectly set up
"""
def isSetupCorrect(config, iconfig): # @devansh, what is the correct/formative way of writing this function definition?
    x = len(config.super_smoothening_kernel)
    if len(iconfig.threshold_redchisq) > 2:
        print(f"iconfig.threshold_redchisq has {len(iconfig.threshold_redchisq)} elements. \
              Elements beyond indices 0 and 1 will not be used")
    elif len(iconfig.threshold_redchisq) == 1:
        print(f"iconfig.threshold_redchisq has only 1 element. Ideally, two separate values \
              are required for single peak and multipeaks respectively. Repeating first value.")
    # TODO: @ ann need to finish this

"""
Function to input light curve data from .fits file
Inputs:
    1. Date of observation
    2. gen -> true = modified 10s cadence light curve. 
       false = default pradhan (1s cadence) light curve
Outputs:
    1. Instance of time of data observations
    2. Photon count in time interval between previous and current time instance
    3. Error associated with photon count
    4. Are previous and/or next day data also available?
    5. Number of datapoints in each of the three days (previous, current and next)
"""
def date_to_data(date: str, gen: bool) -> Tuple[npt.NDArray[np.int32], npt.NDArray[np.float64]]:
    # Set data file location. Modify as per requirement.
    if gen:
        filename = os.path.join(os.path.dirname(__file__),
                                'data', 'Lightcurves',
                                f'gen_{date}.lc')
    else:
        filename = os.path.join(os.path.dirname(__file__),
                                'data', 'XRS_LightCurve_1s',
                                f'sci_xrsf-l2-flx1s_g17_d{date}_v2-2-0.nc')

    # Raise exception if filename does not exist at specified location
    if os.path.isfile(filename) is False:
        raise FileNotFoundError(f"{filename} does not exist")

    # Decompose date string (yyyymmdd) into separate integer variables
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])

    # Initialise flag variables
    prev_day_flag = next_day_flag = False

    # @devansh
    rel = dt(year, month, day) - dt(2017, 1, 1)

    if gen:
        # Import light curve data for current date from filename
        with fits.open(filename) as hdul:
            table: fits.hdu.table.BinTableHDU = hdul.pop(1)
            data = np.array(table.data)
            time = (data['TIME'] - rel.total_seconds()).astype(np.int64)
            counts = data['FLUX'].astype(np.float64)*1e9
            cnterror = data['ERROR'].astype(np.float64)*1e9
        maxcount = np.nanmax(counts)
        # Set number of observations in current date
        n_data = [0, np.sum(~np.isnan(counts)), 0]
        # Set previous and next dates
        prev_dt = dt(year, month, day) - dtt.timedelta(days=1)
        next_dt = dt(year, month, day) + dtt.timedelta(days=1)
        # Set previous and next dates' filenames
        # TODO: Add `if gen` clause
        filename_prev = os.path.join(os.path.dirname(__file__),
                                    'data', 'Lightcurves',
                                    f'gen_{prev_dt.strftime("%Y%m%d")}.lc')
        filename_next = os.path.join(os.path.dirname(__file__),
                                    'data', 'Lightcurves',
                                    f'gen_{next_dt.strftime("%Y%m%d")}.lc')
        
        if os.path.isfile(filename_prev):
            prev_day_flag = True    # Set previous date flag if data is available
            # Import light curve data for previous date from filename
            with fits.open(filename_prev) as hdul:
                table: fits.hdu.table.BinTableHDU = hdul.pop(1)
                data = np.array(table.data)
                time_prev = (data['TIME'] - rel.total_seconds()).astype(np.int64)
                counts_prev = data['FLUX'].astype(np.float64)*1e9
                cnterror_prev = data['ERROR'].astype(np.float64)*1e9

            # Stitch previous date data with current date data
            time = np.concatenate((time_prev, time))
            counts = np.concatenate((counts_prev, counts))
            cnterror = np.concatenate((cnterror_prev, cnterror))
            # Set number of observations in previous date
            n_data[0] = np.sum(~np.isnan(counts_prev))

        #
        if os.path.isfile(filename_next):
            next_day_flag = True    # Set next date flag if data is available
            # Import light curve data for next date from filename
            with fits.open(filename_next) as hdul:
                table: fits.hdu.table.BinTableHDU = hdul.pop(1)
                data = np.array(table.data)
                time_next = (data['TIME'] - rel.total_seconds()).astype(np.int64)
                counts_next = data['FLUX'].astype(np.float64)*1e9
                cnterror_next = data['ERROR'].astype(np.float64)*1e9
            # Stitch next date data with previous+current date data
            time = np.concatenate((time, time_next))
            counts = np.concatenate((counts, counts_next))
            cnterror = np.concatenate((cnterror, cnterror_next))
            # Set number of observations in next date
            n_data[2] = np.sum(~np.isnan(counts_next))
    else:
        dataset = nc.Dataset(filename)
        time = np.array(dataset['time'][:])
        time_correction = time[0]
        time = time - time_correction
        time = np.int32(time[6::10])
        counts = np.array(dataset.variables['xrsb1_flux'][:])
        counts = counts * 1e9
        counts = bin(counts, 10)
        counts[counts <= 0] = np.nan
        cnterror = np.sqrt(counts)
        n_data = [0, np.sum(~np.isnan(counts)), 0]
        maxcount = np.nanmax(counts)
        prev_dt = dt(year, month, day) - dtt.timedelta(days=1)
        next_dt = dt(year, month, day) + dtt.timedelta(days=1)
        # Set previous and next dates' filenames
        filename_prev = os.path.join(os.path.dirname(__file__),
                                    'data', 'XRS_LightCurve_1s',
                                    f'sci_xrsf-l2-flx1s_g17_d{prev_dt.strftime("%Y%m%d")}_v2-2-0.nc')
        filename_next = os.path.join(os.path.dirname(__file__),
                                    'data', 'XRS_LightCurve_1s',
                                    f'sci_xrsf-l2-flx1s_g17_d{next_dt.strftime("%Y%m%d")}_v2-2-0.nc')
        
        if os.path.isfile(filename_prev):
            prev_day_flag = True    # Set previous date flag if data is available
            # Import light curve data for previous date from filename
            dataset = nc.Dataset(filename_prev)
            time_prev = np.array(dataset['time'][:])
            time_prev = time_prev - time_correction
            time_prev = np.int32(time_prev[4::10])
            counts_prev = np.array(dataset.variables['xrsb1_flux'][:]) * 1e9
            counts_prev = bin(counts_prev, 10)
            counts_prev[counts_prev <= 0] = np.nan
            cnterror_prev = np.sqrt(counts_prev)

            # Stitch previous date data with current date data
            time = np.concatenate((time_prev, time))
            counts = np.concatenate((counts_prev, counts))
            cnterror = np.concatenate((cnterror_prev, cnterror))
            # Set number of observations in previous date
            n_data[0] = np.sum(~np.isnan(counts_prev))

        if os.path.isfile(filename_next):
            prev_day_flag = True    # Set previous date flag if data is available
            # Import light curve data for previous date from filename
            dataset = nc.Dataset(filename_next)
            time_next = np.array(dataset['time'][:])
            time_next = time_next - time_correction
            time_next = np.int32(time_next[5::10])
            counts_next = np.array(dataset.variables['xrsb1_flux'][:]) * 1e9
            counts_next = bin(counts_next, 10)
            counts_next[counts_next <= 0] = np.nan
            cnterror_next = np.sqrt(counts_next)

            # Stitch next date data with previous+current date data
            time = np.concatenate((time, time_next))
            counts = np.concatenate((counts, counts_next))
            cnterror = np.concatenate((cnterror, cnterror_next))
            # Set number of observations in next date
            n_data[2] = np.sum(~np.isnan(counts_next))
    
    # Exception checking
    assert time.min() >= -86400, "Time is negative"
    assert time.max() < 172800, "Time is greater than 24 hours"
    # Number of datapoints check
    if (sum(n_data) <= 3*3456 or n_data[1] < 0.4*8640) and (date != '20210507'): # TODO: Find a 'better' heuristic that covers a wider range of dates. Currently, many dates simply don't execute
        print(f'Not enough datapoints in lightcurve {date}: {sum(n_data)}, {n_data[1]}')
        # print(time)
        exit(0)
    # if n_data[1] < 0.6*8640 or (np.nanmax(counts) - np.nanmin(counts)) < 50 or int(date) >= 20220101:
    #     print('Fails aggressive robustness requirements')
    #     exit(0)

    return time, counts, cnterror, [prev_day_flag, next_day_flag], n_data


"""
Interpolate NaN values in a numpy array
Input:
    1. Any one dimensional array (possibly with nans)
Outputs:
    1. Location of nans in input array
    2. ??
"""
def nan_helper(arr): # TODO fill up function definition
                     # 28.05.23 I don't remember what the above comment is about
    return np.isnan(arr), lambda z: z.nonzero()[0]


def bin(arr: npt.NDArray[Any], binning_size: int) -> npt.NDArray[Any]:
    sz = int(len(arr))
    bins = sz // binning_size
    if (sz % bins == 0):
        bins -= 1
    binned = np.zeros(bins + 1)
    for i in range(bins):
        binned[i] = np.nanmean(arr[binning_size * i:binning_size * (i + 1)])
    binned[-1] = np.nanmean(arr[binning_size * bins:])
    return binned


def smoothen(arr: npt.NDArray[Any], smoothening_kernel: int) -> npt.NDArray[Any]:
    return (convolve(arr, Gaussian1DKernel(smoothening_kernel)))#[smoothening_kernel // 2:-smoothening_kernel]


def merge_ranges(index, fmarks, time, threshold):
    for i in range(np.shape(fmarks)[0] - 1):
        if (time[fmarks[i + 1][0]] - time[fmarks[i][-1]]) < threshold:
            index = np.append(index, np.arange(fmarks[i][-1], fmarks[i + 1][0]))
    return index


def remove_ranges(index, time, counts):
    noregiontime = np.delete(time, index)
    noregioncounts = np.delete(counts, index)
    return noregiontime, noregioncounts


def nan_ranges(index, time, counts):
    # Using np.array to copy by value and not copy by reference
    noregiontime = np.array(time)
    noregioncounts = np.array(counts)
    noregioncounts[index] = np.nan
    return noregiontime, noregioncounts


# Signal to Noise Ratio
def get_snr(signal, background):
    # SNR = S*sqrt(duration)/sqrt(S+2B)
    # return np.mean(signal) * np.sqrt(len(counts)) / (np.sqrt(np.mean(signal) + 2 * background))
    return signal / np.sqrt(signal + 2 * background)


# sub-A (Q), A, B, C, M, X
def get_flare_class(peak_count: np.float64) -> str:
    flux = peak_count
    # flare_class_val = np.log10(np.max(flux)) - 1 # TODO: Find more decimal digits accurate `log` algorithm implementation
    # Update 9.6.23 verified this expression
    flare_class_val = np.log10(flux) - 1
    flare_class = 'U'
    if (flare_class_val < 0):
        flare_class = 'sub-A'
    elif (flare_class_val < 1):
        flare_class = 'A' + str(np.int32(flux / 10))
    elif (flare_class_val < 2):
        flare_class = 'B' + str(np.int32(flux / 1e2))
    elif (flare_class_val < 3):
        flare_class = 'C' + str(np.int32(flux / 1e3))
    elif (flare_class_val < 4):
        flare_class = 'M' + str(np.int32(flux / 1e4))
    else:
        flare_class = 'X' + str(np.int32(flux / 1e5))

    return flare_class
