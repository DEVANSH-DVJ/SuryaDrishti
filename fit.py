from dataclasses import dataclass, field
from typing import Tuple

import numpy as np
import numpy.typing as npt
from scipy.special import erf
from lmfit import Model

@dataclass
class PerFitParam:
    Aprime: np.float64
    mu: np.float64
    sigma: np.float64
    tau: np.float64

    def __array__(self) -> np.ndarray:
        return np.array([self.Aprime, self.mu, self.sigma, self.tau])


@dataclass
class FitVar:
    # Fit flag
    flag: bool

    # Fit Parameters
    popt: npt.NDArray[np.float64] = field(repr=False)
    pfp: PerFitParam = field(init=False, repr=False)
    c: np.float64 = field(init=False, repr=False)
    A: np.float64 = field(init=False, repr=False)           # From lmfit
    A_scipy: np.float64 = field(init=False, repr=False)     # From scipy

    # Fit Data
    x: npt.NDArray[np.int32] = field(repr=False)
    y: npt.NDArray[np.float64] = field(repr=False)
    fit: npt.NDArray[np.float64] = field(init=False, repr=False)

    # Reduced Chi-Square
    # redchisq: np.float64 = field(init=False)

    # Pre-Fit Peak Parameters
    pre_fit_peak_time: np.int32 = field(init=False, repr=False)
    pre_fit_start_time: np.int32 = field(init=False, repr=False)
    pre_fit_end_time: np.int32 = field(init=False, repr=False)
    pre_fit_peak_count: np.float64 = field(init=False, repr=False)
    pre_fit_start_count: np.float64 = field(init=False, repr=False)
    pre_fit_end_count: np.float64 = field(init=False, repr=False)

    # Post-Fit Peak Parameters
    post_fit_peak_time: np.int32 = field(init=False,)
    post_fit_start_time: np.int32 = field(init=False, repr=False)
    post_fit_end_time: np.int32 = field(init=False, repr=False)
    post_fit_peak_count: np.float64 = field(init=False)
    post_fit_start_count: np.float64 = field(init=False, repr=False)
    post_fit_end_count: np.float64 = field(init=False, repr=False)

    def __init__(self, flag: bool, popt: npt.NDArray[np.float64], x: npt.NDArray[np.float64], y: npt.NDArray[np.float64], yerr: npt.NDArray[np.float64]) -> None:
        # Fit flag
        self.flag = flag

        # Fit Parameters
        self.popt = popt                                                                # from lmfit
        self.pfp = PerFitParam(*self.popt[0:4])                                         # from lmfit
        self.c = 0                                                                      # overriden to 0 as lmfit separates signal and bg models
        self.A = self.pfp.Aprime * self.pfp.tau / self.pfp.sigma * np.sqrt(2 / np.pi)   # from lmfit

        # Fit Data
        self.x = x                                                                      # time
        self.y = y                                                                      # lmfit curve fit counts
        self.yerr = yerr                                                                # cnterror

        # Calculate flare redchisq and r-squared
        # (This is a complicated way but at least consistently uses lmfit)
        model = Model(lmfit_exp_gaus_single)
        pars = model.make_params()
        # Setting the parameter vary argument as False as optimal argument
        # values have already been calculated in FlareDecomposition()
        pars['Aprime'].set(popt[0], min=0, vary=False)
        pars['mu'].set(popt[1], min=popt[1]-600, max=popt[1]+300, vary=False)
        pars['sigma'].set(popt[2], min=0, vary=False)
        pars['tau'].set(popt[3], min=0, vary=False)
        pars.update(pars)
        result = model.fit(self.y, pars, x=self.x)
        self.fit = result.best_fit
        self.redchisq = result.redchi
        self.rsquared = result.rsquared
        self.fit_result = result

        # Pre-Fit Peak Parameters
        peak_idx = int(np.argmax(self.y))

        self.pre_fit_peak_time = self.x[peak_idx]
        self.pre_fit_start_time = self.x[0]
        self.pre_fit_end_time = self.x[-1]

        self.pre_fit_peak_count = self.y[peak_idx]
        self.pre_fit_start_count = self.y[0]
        self.pre_fit_end_count = self.y[-1]

        # Post-Fit Peak Parameters
        fit_y_10th = (np.max(self.fit) - self.c) / 10 + self.c
        peak_idx = int(np.argmax(self.fit))
        try:
            start_idx = int(np.argmin(np.abs(fit_y_10th - self.fit[:peak_idx])))
        except ValueError:
            print("Post fit start index set to zero")
            start_idx = 0
        try:
            end_idx = int(np.argmin(np.abs(fit_y_10th - self.fit[peak_idx:])) + peak_idx)
        except ValueError:
            print("Post fit end index set to -1")
            end_idx = -1

        self.post_fit_peak_time = self.x[peak_idx]
        self.post_fit_start_time = self.x[start_idx]
        self.post_fit_end_time = self.x[end_idx]

        self.post_fit_peak_count = self.fit[peak_idx]
        if self.post_fit_peak_count < 1:
            print("Post fit peak flux is less than 1")
        self.post_fit_start_count = self.fit[start_idx]
        self.post_fit_end_count = self.fit[end_idx]


"""
Newly defined exponential gaussian fit 
without constant background specifically
to use with `lmfit`
"""
def lmfit_exp_gaus_single(x: np.int32 | npt.NDArray[np.int32], Aprime: np.float64, mu: np.float64, sigma: np.float64, tau: np.float64) -> np.float64 | npt.NDArray[np.float64]:
    pfp = [Aprime, mu, sigma, tau]
    y1 = -(x - pfp[1]) / pfp[3] + pfp[2]**2 / (2 * pfp[3]**2)
    y2 = (x - pfp[1]) / (np.sqrt(2) * pfp[2]) - pfp[2] / (np.sqrt(2) * pfp[3])
    return pfp[0] * np.exp(y1) * (1 + erf(y2))      # 1.06.23 verified this expression
