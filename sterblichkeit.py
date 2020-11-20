#!/usr/bin/env python3

import io
import os
import requests
import sys

import pandas as pd

current_url = 'https://www.bfs.admin.ch/bfsstatic/dam/assets/14940466/master'
history_url = 'https://www.bfs.admin.ch/bfsstatic/dam/assets/12607336/master'


def get(url):
    r = requests.get(url, allow_redirects=True)
    if r.status_code != 200:
        raise ValueError(f'fetch url {url}: status {r.status_code}')
    return r.content.decode('iso-8859-1')


def tidy_csv(text):
    rows = text.splitlines()
    rows = [r.strip() for r in rows]
    rows = [r for r in rows if not r.startswith('#')]
    return '\n'.join(rows)


def as_dataframe(csv_text, sep=';'):
    data = io.StringIO(csv_text)
    return pd.read_csv(data, sep=sep)


def main():

    current_csv_data = get(current_url)
    history_csv_data = get(history_url)

    current_csv_data = tidy_csv(current_csv_data)
    history_csv_data = tidy_csv(history_csv_data)

    current = as_dataframe(current_csv_data)
    history = as_dataframe(history_csv_data)

    print(history)

    # TODO:
    # - figure out max week of current year
    # - use same column headers
    # - merge data frames
    # - calculate...

    return  # FIXME: move further below as data is fetched

    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} csv_file [up to week]')
        sys.exit(1)

    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f'csv file {csv_path} not found')
        sys.exit(2)

    week = 53
    if len(sys.argv) == 3:
        week = int(sys.argv[2])

    data = pd.read_csv(csv_path, sep=';')
    data = data[data['Kalenderwoche'] <= week]
    data = data.filter(items=['KJ', 'Anzahl_Todesfalle'])
    data['Anzahl_Todesfalle'] = data['Anzahl_Todesfalle'].apply(
        float).apply(round).apply(int)
    data = data.groupby('KJ').aggregate({'Anzahl_Todesfalle': sum})

    print(data)

    print('std', data['Anzahl_Todesfalle'].std())
    print('mean', data['Anzahl_Todesfalle'].mean())


if __name__ == '__main__':
    main()
