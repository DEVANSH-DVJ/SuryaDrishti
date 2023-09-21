import csv
import os
import sys

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


def save_new_plot(lc: LightCurve):
    filename = os.path.join(os.path.dirname(__file__),
                            'data', 'XSM_Processed_Plots',
                            f'{lc.config.date}_plot.png')
    plot_all(lc, filename, yscale='log')
    # plot_all(lc, yscale='log')

    for i, region in enumerate(lc.regions):
        filename = os.path.join(os.path.dirname(__file__),
                                'data', 'XSM_Processed_Plots',
                                f'{lc.config.date}_reg{i+1}.png')
        plot_region(region, filename, yscale='linear')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python main.py <date>')
        sys.exit(1)

    config = Config(date=sys.argv[1], gen=True)

    if int(sys.argv[1]) < 20200520:
        iconfig = InternalConfig(init_prominence=4)
    elif int(sys.argv[1]) < 20210520:
        iconfig = InternalConfig(init_prominence=8)
    elif int(sys.argv[1]) < 20220520:
        iconfig = InternalConfig(init_prominence=13)
    else:
        iconfig = InternalConfig(init_prominence=23)

    lc = LightCurve(config, iconfig)
    save_summary(lc)
    save_new_plot(lc)
    sys.exit(0)
