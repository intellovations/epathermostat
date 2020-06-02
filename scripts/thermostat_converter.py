#!/usr/bin/env python
import csv
import glob
import os
import dateutil.parser
from datetime import datetime, timedelta

FIELDNAMES = [
        'datetime',
        'cool_runtime_stg1', 'cool_runtime_stg2', 'cool_equiv_runtime',
        'heat_runtime_stg1', 'heat_runtime_stg2', 'heat_equiv_runtime',
        'emergency_heat_runtime',
        'auxiliary_heat_runtime',
        'temp_in',
        ]


def normalize_utc_offset(utc_offset):
    """
    Normalizes the UTC offset
    Returns the UTC offset based on the string passed in.

    Parameters
    ----------
    utc_offset : str
        String representation of the UTC offset

    Returns
    -------
    datetime timdelta offset
    """
    try:
        if int(utc_offset) == 0:
            utc_offset = "+0"
        delta = dateutil.parser.parse(
            "2000-01-01T00:00:00" + str(utc_offset)).tzinfo.utcoffset(None)
        return delta

    except (ValueError, TypeError, AttributeError) as e:
        raise TypeError("Invalid UTC offset: {} ({})".format(
           utc_offset,
           e))


def main():
    """ This script will convert over old thermostat data files to the new
    EPAThermostat 2.0 format. It should be used for testing only, and is not
    intended for data submissions.
    """

    hour_interval = timedelta(hours=1)

    metadata = {}
    for filename in glob.iglob('metadata*.csv'):
        with open(filename) as metadata_csv:
            metadata_reader = csv.DictReader(metadata_csv)
            for row in metadata_reader:
                metadata[row['interval_data_filename']] = row

    for filename in glob.iglob('thermostat_*.csv'):
        input_filename = filename
        output_filename = os.path.join("new", filename)
        thermostat_id = filename.lstrip('thermostat_')
        thermostat_id = thermostat_id.strip('.csv')
        with open(output_filename, 'w') as outfile:
            csv_out = csv.DictWriter(outfile, FIELDNAMES)
            csv_out.writeheader()

            with open(input_filename) as csvfile:
                thermostat_csv = csv.DictReader(csvfile)
                for row in thermostat_csv:
                    utc_offset = normalize_utc_offset(metadata[input_filename]['utc_offset'])
                    current_datetime = datetime.strptime(row['date'], '%Y-%m-%d')
                    for hour in range(0, 24):

                        current_row = {}
                        current_row['datetime'] = current_datetime + (hour_interval * hour) - utc_offset

                        current_row['cool_runtime_stg2'] = None

                        cool_runtime = row.get('cool_runtime')
                        if cool_runtime is not None and cool_runtime != '':
                            cool_runtime = float(cool_runtime) / 24.0
                        else:
                            cool_runtime = None
                        current_row['cool_runtime_stg1'] = cool_runtime
                        current_row['cool_equiv_runtime'] = None

                        current_row['heat_runtime_stg2'] = None

                        heat_runtime = row.get('heat_runtime')
                        if heat_runtime is not None and heat_runtime != '':
                            heat_runtime = float(heat_runtime) / 24.0
                        else:
                            heat_runtime = None
                        current_row['heat_runtime_stg1'] = heat_runtime
                        current_row['heat_equiv_runtime'] = None

                        header = 'auxiliary_heat_runtime_%02d' % hour
                        current_row['auxiliary_heat_runtime'] = row[header]

                        header = 'emergency_heat_runtime_%02d' % hour
                        current_row['emergency_heat_runtime'] = row[header]

                        header = 'temp_in_%02d' % hour
                        current_row['temp_in'] = row[header]

                        csv_out.writerow(current_row)


if __name__ == '__main__':
    main()
