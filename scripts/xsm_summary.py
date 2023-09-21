import os
from multiprocessing import Pool
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def run(date):
    print(f'Started {date}')
    os.system('python3 {} {}'.format(os.path.join(BASE_DIR, 'main.py'), date))
    print(f'Finished {date}')
    print()


if __name__ == '__main__':
    date_list = []

    # filename = 'XSM_Extracted_LightCurve_list.txt'
    # with open(os.path.join(DATA_DIR, filename)) as f:
    #     for line in f:
    #         date = line.strip()[33:41]
    #         date_list.append(date)

    start_date = date(2019, 9, 12)
    numdays = 224
    for elapseddays in range(numdays):
        cur_date = start_date + timedelta(days=elapseddays)
        str_date = f'{cur_date.year}{cur_date.month:02}{cur_date.day:02}'
        date_list.append(str_date)

    pool = Pool(processes=8)
    pool.map(run, date_list)
