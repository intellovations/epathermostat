from datetime import datetime
import eeweather

import pandas as pd

# This routine is a compact version of code that was originally released as eeweather_wrapper.py
# https://github.com/openeemeter/eemeter/blob/345afcb40ce5786bfbd117cb51536d7ca807a32c/eemeter/weather/eeweather_wrapper.py


def convert_to_farenheit(x):
    return 1.8 * x + 32


def get_indexed_temperatures_eeweather(usaf_id, index):
    if index.shape == (0,):
        return pd.Series([], index=index, dtype=float)
    years = sorted(index.groupby(index.year).keys())
    start = pd.to_datetime(datetime(years[0], 1, 1), utc=True)
    end = pd.to_datetime(datetime(years[-1], 12, 31, 23, 59), utc=True)
    tempC, warnings = eeweather.load_isd_hourly_temp_data(usaf_id, start, end)
    tempC = tempC.resample('H').mean()[index]
    tempF = convert_to_farenheit(tempC)
    return tempF
