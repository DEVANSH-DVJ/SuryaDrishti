import os
from multiprocessing import Pool

from pha_to_lc import write_lc_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PHA_DIR = os.path.join(DATA_DIR, 'XSM_Generated_PHA')
LC_DIR = os.path.join(DATA_DIR, 'XSM_Generated_LightCurve')


def run(date):
    print(date)
    try:
        write_lc_file(os.path.join(PHA_DIR, f'ch2_xsm_{date}_v1.pha'), 1.551, 12.408, os.path.join(LC_DIR, f'gen_{date}.lc'))
    except ValueError:
        print(f'Error: {date}')


if __name__ == '__main__':
    date_list = []

    filename = 'XSM_Generated_PHA_list.txt'
    with open(os.path.join(DATA_DIR, filename)) as f:
        for line in f:
            date = line.strip()[26:34]
            date_list.append(date)

    pool = Pool(processes=8)
    pool.map(run, date_list)
