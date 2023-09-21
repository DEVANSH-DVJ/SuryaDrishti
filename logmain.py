import os
import sys
import csv
import subprocess
from multiprocessing import Pool
import time
from datetime import date, timedelta, datetime
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

from plot import plot_all, plot_region
from sd import Config, InternalConfig, LightCurve

keys = [
    'date',

    'post_fit_start_time',
    'post_fit_start_count',
    'post_fit_peak_time',
    'post_fit_peak_count',
    'post_fit_end_time',
    'post_fit_end_count',

    'complex_region',
    'active_region',
    'multi_flare_region_flag',
    'multi_flare_unresolved_flag',
    'flare_class_with_bg',
    'flare_class_without_bg',
    'mean_background',

    'flare amplitude',
    'fit_param_Aprime',
    'fit_param_mu',
    'fit_param_sigma',
    'fit_param_tau',
    'redchisq',
    'rsquared',
    'snr',

    'pre_fit_start_time',
    'pre_fit_start_count',
    'pre_fit_peak_time',
    'pre_fit_peak_count',
    'pre_fit_end_time',
    'pre_fit_end_count',

    'flag'
]


def save_summary(lc: LightCurve):
    filename = os.path.join(os.path.dirname(__file__),
                            'data', 'XSM_Processed_Summary',
                            f'{lc.config.date}_summary.csv')

    data = lc.dump()
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)


def save_plot(lc: LightCurve):
    filename = os.path.join(os.path.dirname(__file__),
                            'data', 'XSM_Processed_Plots',
                            f'{lc.config.date}_plot.png')
    plot_all(lc, filename, yscale='log')

    for i, region in enumerate(lc.regions):
        filename = os.path.join(os.path.dirname(__file__),
                            'data', 'XSM_Processed_Plots',
                            f'{lc.config.date}_reg{i+1}.png')
        plot_region(region, filename, yscale='linear')


def run(curdate):
    config = Config(date=curdate, gen=glob.gen, super_smoothening_kernel=glob.super_smoothening_kernel, threshold_mergepeaks=glob.threshold_mergepeaks, 
                    threshold_duration=glob.threshold_duration, threshold_snr_region=glob.threshold_snr_region, threshold_upturns=glob.threshold_upturns,
                    nsigma=glob.nsigma)

    # if int(curdate) < 20200520:
    #     iconfig = InternalConfig(init_prominence=4, aggression=glob.aggression)
    # elif int(curdate) < 20210520:
    #     iconfig = InternalConfig(init_prominence=8)
    if int(curdate) < 20210520:
        iconfig = InternalConfig(init_prominence=4, aggression=glob.aggression)
    elif int(curdate) < 20220520:
        iconfig = InternalConfig(init_prominence=13)
    else:
        iconfig = InternalConfig(init_prominence=23)

    try:
        lc = LightCurve(config, iconfig)
    except (SystemExit, FileNotFoundError) as e:
        print(f'Lightcurve {curdate} aborted')
        print(f'Lightcurve {curdate} aborted', file=sys.stderr)
        return
    save_summary(lc)
    try:
        save_plot(lc)
    except IndexError:
        print(f'Lightcurve {curdate} save plot failed', file=sys.stderr)
    print(f'Finished {curdate}')
    print()


"""
Set up execution
"""
n_proc = 4                              # Number of processors to be used
glob = Config(
    date                     = 'NA',
    gen                      = True,
    super_smoothening_kernel = [10,10],
    threshold_mergepeaks     = 120,
    threshold_duration       = 120,
    threshold_snr_region     = 1,
    threshold_upturns        = 3,
    nsigma                   = 0.3
    )
glob.aggression              = 0.7      # Only changes for < 20200520
start_date = date(2019, 9, 12)
numdays = 1157
# prominence: 3-4; aggresion: 0.6-0.7

if __name__ == '__main__':
    """
    Valid simulation?
    """
    if len(sys.argv) != 2:
        print('Usage: python3 logmain.py <output_root>')
        sys.exit(1)

    date_list = []

    """
    Check whether directory exists else create it
    """
    output_root = sys.argv[1]
    dirname = os.path.join(BASE_DIR, 'data', 'Runs', str(output_root))
    Path(dirname).mkdir(parents=False, exist_ok=False)

    dirplots = os.path.join(BASE_DIR, 'data', 'XSM_Processed_Plots')
    Path(dirplots).mkdir(parents=False, exist_ok=True)
    dirsummary = os.path.join(BASE_DIR, 'data', 'XSM_Processed_Summary')
    Path(dirsummary).mkdir(parents=False, exist_ok=True)

    t0 = time.time()
    """
    Parallel run
    """
    for elapseddays in range(numdays):
        cur_date = start_date + timedelta(days=elapseddays)
        str_date = f'{cur_date.year}{cur_date.month:02}{cur_date.day:02}'
        date_list.append(str_date)

    pool = Pool(processes = n_proc)
    pool.map(run, date_list)

    os.system('./scripts/collect_xsm_summary.sh')
    os.system('mv {} {}'.format(os.path.join(BASE_DIR, 'data', 'all.csv'),
                                dirname))
    t1 = time.time()
    os.system('mv {} {}'.format(os.path.join(BASE_DIR, 'data', 'XSM_Processed_Plots'),
                                dirname))
    os.system('mv {} {}'.format(os.path.join(BASE_DIR, 'data', 'XSM_Processed_Summary'),
                                dirname))

    """
    Create log file
    """
    now = datetime.now()
    param_fname = f'{dirname}/params.log'
    sd_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], 
                                      cwd=BASE_DIR).decode('ascii').strip()

    dash_line = '-----------------------------' + '\n'
    empty_line = '\n'

    line00 = 'Date Parameters' + '\n'
    line01 = 'First date : ' + str(start_date) + '\n'
    line02 = 'Number of days : ' + str(numdays) + '\n'
    line03 = 'Last date : ' + str(start_date + timedelta(days=numdays-1)) + '\n'

    line0 = 'Config Parameters' + '\n'
    line1 = 'gen, ' + str(glob.gen) + '\n'
    line2 = 'super_smoothening_kernel, ' + str(glob.super_smoothening_kernel) + '\n'
    line3 = 'threshold_mergepeaks, ' + str(glob.threshold_mergepeaks) + '\n'
    line4 = 'threshold_duration, ' + str(glob.threshold_duration) + '\n'
    line5 = 'threshold_snr_region, ' + str(glob.threshold_snr_region) + '\n'
    line6 = 'threshold_upturns, ' + str(glob.threshold_upturns) + '\n'
    line7 = 'nsigma, ' + str(glob.nsigma) + '\n'
    line8 = 'aggression (< 20200520), ' + str(glob.aggression) + '\n'
    
    line9 = 'RunTime Information' + '\n'
    line10 = str(now) + ' : creation date' + '\n'
    line11 = sd_hash + ' : SD commit' + '\n'

    line12 = 'Total runtime (s) : ' + str(round((t1 - t0), 2)) + '\n'
    line13 = 'Number of processors : ' + str(n_proc) + '\n'
    line14 = 'BASE_DIR/' + str(output_root) + '/XSM_Processed_ Plots(.png), Summary(.csv)'

    with open(f'{dirname}/logfile.log', 'w') as out:
        out.writelines([line00, dash_line, line01, line02, line03, empty_line,
                        line0, dash_line, line1, line2, line3, line4,
                        line5, line6, line7, line8, empty_line,
                        line9, dash_line, line10, line11, empty_line,
                        line12, line13, empty_line, line14])
