from thermostat.importers import from_csv
from thermostat.util.testing import get_data_path
import datetime

import pandas as pd

import pytest

from .fixtures.thermostats import (
        thermostat_type_1,
        thermostat_type_1_utc,
        thermostat_type_1_too_many_minutes,
        )

def test_import_csv(thermostat_type_1):

    def assert_is_series_with_shape(series, shape):
        assert isinstance(series, pd.Series)
        assert series.shape == shape

    assert_is_series_with_shape(thermostat_type_1.cool_runtime_daily, (1461,))
    assert_is_series_with_shape(thermostat_type_1.heat_runtime_daily, (1461,))

    assert_is_series_with_shape(thermostat_type_1.cool_runtime_hourly, (35064,))
    assert_is_series_with_shape(thermostat_type_1.heat_runtime_hourly, (35064,))

    assert_is_series_with_shape(thermostat_type_1.auxiliary_heat_runtime, (35064,))
    assert_is_series_with_shape(thermostat_type_1.emergency_heat_runtime, (35064,))

    assert_is_series_with_shape(thermostat_type_1.temperature_in, (35064,))
    assert_is_series_with_shape(thermostat_type_1.temperature_out, (35064,))

def test_too_many_minutes(thermostat_type_1_too_many_minutes):
    # None of the thermostats in this list should import
    assert len(thermostat_type_1_too_many_minutes) == 0
