import csv
import os
from datetime import date, timedelta

import pandas as pd
from astropy.io import fits

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def write_csv(data, filename):
    with open(os.path.join(DATA_DIR, filename), 'w') as f:
        writer = csv.DictWriter(f, data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def open_lc(filename):
    with fits.open(os.path.join(DATA_DIR, filename)) as hdul:
        lc = pd.DataFrame(hdul[1].data)
    return lc


if __name__ == '__main__':
    status = {}
    for val in daterange(date(2019, 9, 1), date(2022, 12, 31)):
        status[val] = {
            'year': val.year,
            'month': val.month,
            'day': val.day,
            'zip': 0,
            'lc': 0,
            'size': 0,
            'max': 0,
        }

    filename = 'XSM_Data_list.txt'
    with open(os.path.join(DATA_DIR, filename)) as f:
        for line in f:
            year = int(line.strip()[17:21])
            month = int(line.strip()[21:23])
            day = int(line.strip()[23:25])
            ind = date(year, month, day)

            status[ind]['zip'] = 1

    filename = 'XSM_Extracted_LightCurve_list.txt'
    with open(os.path.join(DATA_DIR, filename)) as f:
        for line in f:
            year = int(line.strip()[33:37])
            month = int(line.strip()[37:39])
            day = int(line.strip()[39:41])
            ind = date(year, month, day)

            assert status[ind]['zip'] == 1
            status[ind]['lc'] = 1

            lc = open_lc(line.strip())
            status[ind]['size'] = lc.shape[0]
            status[ind]['max'] = lc['RATE'].max().round(2)

    write_csv(list(status.values()), 'xsm_status.csv')
