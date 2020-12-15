#!/usr/bin/env python3

import io
import requests

import pandas as pd

current_url = 'https://www.bfs.admin.ch/bfsstatic/dam/assets/15204846/master'
history_url = 'https://www.bfs.admin.ch/bfsstatic/dam/assets/12607336/master'

population = {
    2010: 7785806,
    2011: 7870134,
    2012: 7954662,
    2013: 8039060,
    2014: 8139631,
    2015: 8237666,
    2016: 8327126,
    2017: 8419550,
    2018: 8484130,
    2019: 8544527,
    2020: 8655118,
}


def get_text(url):
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

    current_csv_data = get_text(current_url)
    history_csv_data = get_text(history_url)

    current_csv_data = tidy_csv(current_csv_data)
    history_csv_data = tidy_csv(history_csv_data)

    current = as_dataframe(current_csv_data)
    history = as_dataframe(history_csv_data)

    current = pd.DataFrame({
        'year': 2020,
        'week': current['Woche'],
        'age': current['Alter'],
        'deads': current['AnzTF_HR'],
    })

    history = pd.DataFrame({
        'year': history['KJ'],
        'week': history['Kalenderwoche'],
        'age': history['Alter'],
        'deads': history['Anzahl_Todesfalle'],
    })

    current['deads'] = pd.to_numeric(current['deads'], errors='coerce')
    current = current[current['deads'].notnull()]
    max_week = max(current['week'])

    history = history[history['week'] <= max_week]

    data = pd.concat([history, current])

    data['pop'] = data['year'].map(population)
    data['up_to_week'] = max_week

    data = data.groupby('year').aggregate({
        'up_to_week': max,
        'deads': sum,
        'pop': max
    })
    data['rate'] = data['deads'] / data['pop']
    data['%'] = (data['deads'] / data['pop']) * 100
    print(data)


if __name__ == '__main__':
    main()
