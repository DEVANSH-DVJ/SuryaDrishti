import datetime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MaxNLocator
from matplotlib.offsetbox import AnchoredText

from sd import LightCurve, Region, Flare
from fit import lmfit_exp_gaus_single

plt.rcParams.update({'font.size': 22, 'lines.linewidth': 3})

"""
Old plot for plotting light curve
Inputs:
    1. LightCurve object
    2. Log or linear yscale
Input (optional):
    1. Filename if plot needs to be saved
"""
def plot_lc(lc: LightCurve, filename: str | None = None, yscale: str = 'log'):
    plt.figure(dpi=100, figsize=(19.2, 7.2))

    plt.tick_params(which='major', width=2)
    plt.tick_params(which='major', length=7)
    plt.tick_params(which='minor', length=4)
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator())

    plt.title(f'Light Curve {lc.config.date}')
    plt.ylabel('Flux (nW/m$^{2}$)')
    plt.xlabel('Time (s)')

    plt.plot(lc.pptime, lc.ppcounts, c='c', label='data')

    plt.scatter(lc.pptime[lc.scpeaks], lc.ppcounts[lc.scpeaks], c='r', s=30, zorder=11)
    plt.plot(lc.bgtime, lc.bgcounts, c='g', alpha=0.4, label='ss bg')

    plt.margins(x=0)
    if yscale == 'linear' or yscale == 'log':
        plt.yscale(yscale)
    else:
        print('yscale must be either linear or log. Default: linear')

    if filename is not None:
        plt.savefig(filename, bbox_inches='tight', dpi=150)
        plt.close()
    else:
        plt.show()

"""
Old plot for plotting individual regions in light curve
Inputs:
    1. LightCurve object
    2. Log or linear yscale
Input (optional):
    1. Filename if plot needs to be saved
"""
def plot_lc_regions(lc: LightCurve, filename: str | None = None, yscale: str = 'log'):
    plt.figure(dpi=100, figsize=(19.2, 7.2))

    plt.tick_params(which='major', width=2)
    plt.tick_params(which='major', length=7)
    plt.tick_params(which='minor', length=4)
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator())

    plt.title(f'Lightcurve {lc.config.date} Identified Regions')
    plt.ylabel('Flux (nW/m$^{2}$)')
    plt.xlabel('Time (s)')

    mu = np.mean(lc.bgcounts)
    sigma = np.std(lc.bgcounts)
    x = lc.pptime
    y = lc.ppcounts
    plt.plot(x, y, alpha=0.3)

    for i in range(len(lc.llist)):
        index = np.sort(np.array(lc.llist[i]))
        x = (lc.pptime[index])
        y = lc.ppcounts[index]
        plt.plot(x, y, c='b')
        plt.axvspan(x[0], x[-1], alpha=0.1, color='orange')
        plt.axvline(x[0], alpha=0.1, color='orange')
        plt.axvline(x[-1], alpha=0.1, color='orange')
        # plt.text(x[-1], np.nanmax(lc.ppcounts) * 0.8, f'Region {i+1}', rotation=-90, va='center', fontsize=14, ha='left')
        plt.text(x[-1], np.nanmax(lc.ppcounts) * 0.7, f'Region {i+1} ({lc.regions[i].numflares})', rotation=-90, va='center', fontsize=14, ha='left')

    plt.text(2000, np.nanmax(lc.ppcounts) * 0.95, f'#Flares: {lc.numflares}', va='center', fontsize=14, ha='left')

    plt.margins(x=0)
    if yscale == 'linear' or yscale == 'log':
        plt.yscale(yscale)
    else:
        print('yscale must be either linear or log. Default: linear')

    if filename is not None:
        plt.savefig(filename, bbox_inches='tight', dpi=150)
        plt.close()
    else:
        plt.show()

"""
New plot to encapsulate LightCurve, Background subtracted light curve, and Region decomposition
Input:
    1. LightCurve object
Inputs (optional):
    1. Filename if plots need to be saved
    2. Log or linear yscale
"""
def plot_all(lc: LightCurve, filename: str | None = None, yscale: str = 'log'):
    fig, axs = plt.subplots(nrows=3, dpi=100, figsize=(19.2, 12.0))
    plt.subplots_adjust(hspace=0.05)

    for ax in axs:
        ax.tick_params(which='major', width=2)
        ax.tick_params(which='major', length=7)
        ax.tick_params(which='minor', length=4)
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.set_ylabel('Flux (nW/m$^{2}$)')
        ax.set_xmargin(0)

    axs[0].set_title(f'Lightcurve {lc.config.date}')
    axs[0].set_xticklabels([])
    axs[1].set_xticklabels([])
    axs[2].set_xlabel('Time (s)')

    # ---------------------------------------------------
    axs[0].plot(lc.pptime, lc.ppcounts, c='c', label='Light curve')
    axs[0].scatter(lc.pptime[lc.scpeaks], lc.ppcounts[lc.scpeaks], c='r', s=30, zorder=11, label='Scipy peaks')
    allowed_indices_pp = np.where((lc.pptime>0) & (lc.pptime<86400))
    axs[0].plot(lc.bgtime, lc.tmp_bgcounts[allowed_indices_pp], c='coral', alpha=0.4, label='BG 1')
    axs[0].plot(lc.bgtime, lc.bgcounts, c='deeppink', alpha=0.4, label='BG 2')
    axs[0].legend(fontsize=16, loc='upper right')
    axs[0].set_yscale('log')

    # ---------------------------------------------------
    mu = np.mean(lc.bgcounts)
    sigma = np.std(lc.bgcounts)
    x = lc.pptime
    y = np.array(lc.nobgcounts)
    axs[1].plot(x, lc.nobgcounts, c='k', alpha=0.3)
    axs[1].plot(x, np.ones(len(x)) * lc.config.nsigma * sigma, '--', c='limegreen', alpha=0.7)
    z = np.where(y > lc.config.nsigma * sigma)[0]
    z2 = np.where(y <= lc.config.nsigma * sigma)[0]
    y[z2] = np.nan
    axs[1].plot(x, y, c='k')
    axs[1].text(x[-1], lc.config.nsigma * sigma, 'n$\sigma_{BG}$', va='bottom', fontsize=14, ha='right')
    axs[1].set_yscale('log')

    # ---------------------------------------------------
    x = lc.pptime
    y = lc.ppcounts
    axs[2].plot(x, y, alpha=0.3)
    axs[2].set_xlim(left=x[0], right=x[-1])

    for i in range(len(lc.llist)):
        index = np.sort(np.array(lc.llist[i]))
        x = (lc.pptime[index])
        y = lc.ppcounts[index]
        axs[2].plot(x, y, c='b')
        axs[2].axvspan(x[0], x[-1], alpha=0.1, color='orange')
        axs[2].axvline(x[0], alpha=0.1, color='orange')
        axs[2].axvline(x[-1], alpha=0.1, color='orange')
        axs[2].text(x[-1], np.nanmax(lc.ppcounts) * 0.95, f'Group {i+1}', rotation=-90, va='top', fontsize=14, ha='left')  # Commentable
        # axs[2].text(x[-1], np.nanmax(lc.ppcounts) * 0.95, f'Group {i+1} ({lc.regions[i].numflares})', rotation=-90, va='top', fontsize=14, ha='left')    # Commentable
    axs[2].set_yscale('log')
    # plt.text(2000, np.nanmax(lc.ppcounts) * 0.95, f'#Flares: {lc.numflares}', va='center', fontsize=14, ha='left')  # Commentable

    # --------------------------------------------------
    
    if yscale == 'linear' or yscale == 'log':
        for ax in axs:
            ax.set_yscale(yscale)
    else:
        print('yscale must be either linear or log. Default: linear')

    if filename is not None:
        plt.savefig(filename, bbox_inches='tight', dpi=100)
        plt.close()
    else:
        plt.show()

"""
Individual flares decomposed in a given region
Input:
    1. Region object
Inputs (optional):
    1. Filename if plots need to be saved
    2. Linear or log yscale
"""
def plot_region(region: Region, filename: str | None = None, yscale: str = 'linear'):
    plt.style.use('seaborn-bright')
    fig, axs = plt.subplots(nrows=2, figsize=(9.6, 9.6), gridspec_kw={'height_ratios': [3, 1]})
    axs[0].set_title(f'Light Curve {region.date}')
    plt.subplots_adjust(hspace=.0)
    for ax in axs:
        ax.tick_params(which='major', width=1)
        ax.tick_params(which='major', length=4)
        ax.set_xmargin(0)

    axs[0].minorticks_on()
    axs[0].set_xticklabels([])
    axs[0].tick_params(axis='x', direction='in')
    axs[1].set_xlabel('Time (s)')
    linestyle = {"elinewidth":1, "capsize":0, "ecolor":"grey"}

    axs[0].errorbar(region.time, region.counts, yerr=region.cnterror, 
                    fmt='D', ms=3, c='navy', label='data', **linestyle)
    axs[0].plot(region.time, region.fit_result.best_fit, lw=3, c='deeppink', label='fit')
    comps = region.fit_result.eval_components()
    # axs[0].plot([],[])  # To cycle through first colour (blue)
    for name, comp in comps.items():
        axs[0].plot(region.time, comp, '--', label=name, lw=2)
    axs[0].set_ylabel('Flux (nW/m$^2$)')
    axs[0].legend(fontsize=16, ncol=2)
    # TODO: Add more attribute information about region to plot
    xlen = region.time[-1] - region.time[0]
    ylen = np.max(region.counts) - np.min(region.counts)
    axs[0].text(region.time[0] + 0.05 * xlen, 0.9 * np.nanmax(region.counts + region.cnterror), 
                f'$R^2$: {region.fit_result.rsquared.round(2)}\n$\chi^2_r$: {region.fit_result.redchi.round(2)}', 
                fontsize=16, ha='left')

    # -------------------------------------
    ydata = (region.counts - region.fit_result.best_fit)
    # axs[1].errorbar(region.time, (ydata)/np.std(ydata), yerr=region.cnterror/np.std(ydata), fmt='D', ms=3, c='blue', **linestyle)
    axs[1].scatter(region.time, (ydata)/np.nanstd(ydata), c='navy', s=3, marker='D')
    axs[1].axhline(np.nanmean((ydata)/np.nanstd(ydata)), linestyle='--', lw=1, c='k')
    axs[1].set_xlim(left=region.time[0], right=region.time[-1])
    axs[1].set_ylabel('(data-fit)/$\sigma$')
    axs[1].set_yticks([-3,0,3])
    axs[1].set_yticklabels([-3,0,3])
    axs[1].set_ylim(bottom=-5,top=5)  # To set ylim on error plot
    # -------------------------------------
    if yscale == 'linear' or yscale == 'log':
        axs[0].set_yscale(yscale)
    else:
        print('yscale must be either linear or log. Default: linear')

    if filename is not None:
        plt.savefig(filename, bbox_inches='tight', dpi=100)
        plt.close()
    else:
        plt.show()

"""
Plotting a flare with all relevant information
Note that the counts associated with the flare are
an estimate from the flare decomposition step under
the fast-rise, slow-decay model
Input:
    1. Flare object
Input (optional):
    1. Filename if plot needs to be saved
"""
def plot_flare(flare: Flare, filename: str | None = None):
    fig, axs = plt.subplots(2, figsize=(9.6, 9.6), gridspec_kw={'height_ratios': [3, 1]})

    # axs[0].set_title(f'Flare at t = {flare.fit.post_fit_peak_time}s')
    plt.xlabel('Time (s)')
    plt.subplots_adjust(hspace=.0)
    linestyle = {"elinewidth":1, "capsize":0, "ecolor":"grey"}
    plt.setp(axs[0].get_xticklabels(), visible=False)

    f = flare.fit
    xt = flare.time - flare.fit.post_fit_peak_time
    yt = flare.counts

    # axs[0].set_title(f'Flare at {f.post_fit_peak_time}s in light curve {flare.date}')

    axs[0].errorbar(xt, yt, yerr=flare.cnterror, fmt='D', ms=3, c='blue', **linestyle)
    at = AnchoredText(f'Class: {flare.flare_class_without_bg}\nSNR: {flare.snr:.2f}', \
                     prop=dict(size=18, color='black'), frameon=False, loc='upper left')
    at.patch.set_boxstyle('round,pad=0.,rounding_size=0.2')
    axs[0].add_artist(at)
    at = AnchoredText(f'{flare.date[:4]}-{flare.date[4:6]}-{flare.date[-2:]} UT{str(datetime.timedelta(seconds=int(f.post_fit_peak_time)))[:-3]:0>5}', \
            prop=dict(size=18, color='black'), frameon=False, loc='upper right')
    at.patch.set_boxstyle('round,pad=0.,rounding_size=0.2')
    axs[0].add_artist(at)

    for ax in axs:
        ax.tick_params(which='major', width=1)
        ax.tick_params(which='major', length=4)
        ax.margins(x=0)
    axs[0].set_ylabel('Flux (nW/m$^2$)')
    axs[1].set_ylabel('Residual ((o-f)/$\sigma$)')
    #axs[1].set_ylabel('Relative\nError (%)')
    axs[1].set_ylim(bottom=-4,top=4)

    range = (np.max(yt) - np.min(yt))/10
    axs[0].scatter(f.post_fit_start_time - f.post_fit_peak_time, \
        f.post_fit_start_count, c='k', s=30, zorder=15)
    axs[0].vlines(x=f.post_fit_start_time - f.post_fit_peak_time, \
        ymin=f.post_fit_start_count - range, \
            ymax=f.post_fit_start_count + range, color='k', linestyle='dotted', linewidth=2)
    axs[0].scatter(f.post_fit_end_time - f.post_fit_peak_time, \
        f.post_fit_end_count, c='k', s=30, zorder=15)
    axs[0].vlines(x=f.post_fit_end_time - f.post_fit_peak_time, \
        ymin=f.post_fit_end_count - range, \
            ymax=f.post_fit_end_count + range, color='k', linestyle='dotted', linewidth=2)

    yfit = f.fit
    axs[0].plot(xt, yfit, c='r', zorder=10, lw=3)
    axs[0].tick_params(axis='x', direction='in')
    axs[1].errorbar(xt, (yt-yfit)/np.std(yt-yfit), yerr=flare.cnterror/np.std(yt-yfit), fmt='D', ms=3, c='blue', **linestyle)
    axs[1].axhline(np.mean((yt-yfit)/np.std(yt-yfit)), linestyle='--', lw=1, c='navy')

    plt.show()

###
#
###

def plot_threes(flares):
    if len(flares) != 4:
        print("Need to call function with three flare objects as argument")
        return

    fig, axs = plt.subplots(ncols=4, figsize=(21.6, 5.4))
    axs[0].set_ylabel('Flux (nW/m$^2$)')
    # axs[1].set_xlabel('Time (s)')
    # fig.subxlabel('Time (s)')
    plt.subplots_adjust(wspace=0.15)
    linestyle = {"elinewidth":0.5, "capsize":0, "ecolor":"grey"}

    for i, flare in enumerate(flares):
        # if np.max(flare.counts) > 1000:
        axs[i].set_xlabel('Time (s)')
        f = flare.fit
        xt = flare.time - flare.fit.post_fit_peak_time
        yt = flare.counts

        axs[i].errorbar(xt, yt, yerr=flare.cnterror, fmt='D', ms=3, c='blue', **linestyle)
        at = AnchoredText(f'{flare.flare_class_without_bg}\n{flare.snr:.2f}', \
                        prop=dict(size=14, color='black'), frameon=False, loc='upper left')
        at.patch.set_boxstyle('round,pad=0.,rounding_size=0.2')
        axs[i].add_artist(at)
        at = AnchoredText(f'{flare.date[:4]}-{flare.date[4:6]}-{flare.date[-2:]} UT{str(datetime.timedelta(seconds=int(f.post_fit_peak_time)))[:-3]:0>5}', \
                prop=dict(size=14, color='black'), frameon=False, loc='upper right')
        at.patch.set_boxstyle('round,pad=0.,rounding_size=0.2')
        axs[i].add_artist(at)

        for ax in axs:
            ax.tick_params(which='major', width=1)
            ax.tick_params(which='major', length=4)
            ax.margins(x=0)

        range = (np.max(yt) - np.min(yt))/10
        axs[i].scatter(f.post_fit_start_time - f.post_fit_peak_time, \
            f.post_fit_start_count, c='k', s=30, zorder=15)
        axs[i].vlines(x=f.post_fit_start_time - f.post_fit_peak_time, \
            ymin=f.post_fit_start_count - range, \
                ymax=f.post_fit_start_count + range, color='k', linestyle='--', linewidth=3, zorder=15)
        axs[i].scatter(f.post_fit_end_time - f.post_fit_peak_time, \
            f.post_fit_end_count, c='k', s=30, zorder=15)
        axs[i].vlines(x=f.post_fit_end_time - f.post_fit_peak_time, \
            ymin=f.post_fit_end_count - range, \
                ymax=f.post_fit_end_count + range, color='k', linestyle='--', linewidth=3, zorder=15)
        # axs[i].set_xlim([f.post_fit_start_time, f.post_fit_end_time] - f.post_fit_peak_time)

        yfit = f.fit
        axs[i].plot(xt, yfit, c='r', zorder=10, lw=3)
        axs[i].tick_params(axis='x', direction='in')
        xlim = min(f.post_fit_peak_time - flare.time[0], flare.time[-1] - f.post_fit_peak_time)
        axs[i].set_xlim([-xlim, xlim])
        # axs[i].yaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
        if (flare.multi_flare_region == True):
            axs[i].set_facecolor('ivory')

    plt.show()

###
def plot_three_regions(regions):
    if len(regions) != 4:
        print("Need to call function with three region objects as argument")
        return
    
    fig, axsarr = plt.subplots(nrows=2, ncols=4, figsize=(21.6, 6.2), gridspec_kw={'height_ratios': [3, 1]})
    axsarr[0, 0].set_ylabel('Flux (nW/m$^2$)')
    axsarr[1, 0].set_ylabel('(data-fit)/$\sigma$')
    # fig.supxlabel('Time (s)')
    plt.subplots_adjust(wspace=0.15) 
    plt.subplots_adjust(hspace=.0)
    linestyle = {"elinewidth":0.5, "capsize":0, "ecolor":"grey"}
    
    plt.style.use('seaborn-bright')
    # axs[0].set_title(f'Flaring duration in light curve {region.date}')
    for i, region in enumerate(regions):
        axs = axsarr[:,i]
        for ax in axs:
            ax.tick_params(which='major', width=1)
            ax.tick_params(which='major', length=4)
            ax.set_xmargin(0)

        axs[0].minorticks_on()
        axs[0].set_xticklabels([])
        axs[0].tick_params(axis='x', direction='in')
        if np.nanmax(region.counts) > 1200:
            axs[1].set_xlabel('Time (s)')

        axs[0].errorbar(region.time, region.counts, yerr=region.cnterror, 
                        fmt='D', ms=2, c='navy', label='data', **linestyle)
        axs[0].plot(region.time, region.fit_result.best_fit, lw=3, c='deeppink', label='fit')
        comps = region.fit_result.eval_components()
        # axs[0].plot([],[])  # To cycle through first colour (blue)
        for name, comp in comps.items():
            axs[0].plot(region.time, comp, '--', label=name, lw=2)
        # axs[0].set_ylabel('Flux (nW/m$^2$)')
        # axs[0].legend(fontsize=16, ncol=2)
        # TODO: Add more attribute information about region to plot
        xlen = region.time[-1] - region.time[0]
        ylen = np.max(region.counts) - np.min(region.counts)
        axs[0].text(region.time[0] + 0.05 * xlen, 0.84 * np.nanmax(region.counts + region.cnterror), 
                    f'$R^2$: {region.fit_result.rsquared.round(2)}\n$\chi^2_r$: {region.fit_result.redchi.round(2)}', 
                    fontsize=14, ha='left')
        axs[0].text(region.time[-1] - 0.05 * xlen, 0.89 * np.nanmax(region.counts + region.cnterror), 
                    f'{region.date[:4]}-{region.date[4:6]}-{region.date[6:]}', 
                    fontsize=14, ha='right')

        # -------------------------------------
        ydata = (region.counts - region.fit_result.best_fit)
        # axs[1].errorbar(region.time, (ydata)/np.std(ydata), yerr=region.cnterror/np.std(ydata), fmt='D', ms=3, c='blue', **linestyle)
        axs[1].scatter(region.time, (ydata)/np.nanstd(ydata), c='navy', s=2, marker='D')
        axs[1].axhline(np.nanmean((ydata)/np.nanstd(ydata)), linestyle='--', lw=2, c='k')
        axs[1].set_xlim(left=region.time[0], right=region.time[-1])
        # axs[1].set_ylabel('(data-fit)/$\sigma$')
        axs[1].set_yticks([-3,0,3])
        axs[1].set_yticklabels([-3,0,3])
        axs[1].set_ylim(bottom=-5,top=5)  # To set ylim on error plot

    plt.show()
