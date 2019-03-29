import logging
import json
from pkg_resources import resource_stream
from eeweather import (
        get_isd_file_metadata,
        zcta_to_lat_long,
        rank_stations,
        select_station)
from eeweather.exceptions import (
        UnrecognizedZCTAError,
        UnrecognizedUSAFIDError)

logging.getLogger(__name__)


with resource_stream('thermostat.resources', 'zipcode_usaf_station.json') as fh:
    zipcode_usaf_json = fh.read()

zipcode_usaf = json.loads(zipcode_usaf_json)
QUALITY_SORT = ['high', 'medium', 'low']


def _get_closest_station_by_zipcode_ranked(zipcode, rank):
    lat, lon = zcta_to_lat_long(zipcode)
    station_ranking = rank_stations(lat, lon)
    station_ranking = station_ranking.sort_values(by=['distance_meters', 'rough_quality'])
    station, warnings = select_station(station_ranking, rank=rank)

    return station, warnings, lat, lon


def get_closest_station_by_zipcode(zipcode):
    """ Look up the station by zipcode from eeweather
    :zipcode:  String
    :returns:  Station

    """
    station_lookup_method_zipcode = lookup_usaf_station_by_zipcode(zipcode)
    try:
        rank = 0
        finding_station = True
        while finding_station:
            rank = rank + 1
            station, warnings, lat, lon = _get_closest_station_by_zipcode_ranked(zipcode, rank)
            if str(station)[0] != 'A':
                finding_station = False

        isd_metadata = get_isd_file_metadata(str(station))
        if len(isd_metadata) == 0:
            logging.warningg("Zipcode %s mapped to station %s, but no ISD metadata was found." % (zipcode, station))
            return station_lookup_method_zipcode

    except UnrecognizedUSAFIDError as e:
        logging.warning("Closest station %s is unrecognized. Using backup-method station %s instead." % (
            str(station),
            station_lookup_method_zipcode))
        return station_lookup_method_zipcode

    except UnrecognizedZCTAError as e:
        logging.warning("Unrecognized ZCTA %s" % e)
        return None

    if str(station) != station_lookup_method_zipcode:
        logging.debug("Previously would have selected station %s instead of %s for zip code %s" % (
            station_lookup_method_zipcode,
            str(station),
            zipcode))

    if warnings:
        logging.warning("Station %s is %d meters over maximum %d meters (%d meters) (zip code %s is at lat/lon %f, %f)" % (
            str(station),
            int(warnings[0].data['distance_meters'] - warnings[0].data['max_distance_meters']),
            int(warnings[0].data['max_distance_meters']),
            int(warnings[0].data['distance_meters']),
            zipcode,
            lat,
            lon,
            ))
        logging.warning("Closest station %s is too far. Using backup-method station %s instead." % (
            str(station),
            station_lookup_method_zipcode))
        return station_lookup_method_zipcode

    return str(station)


def lookup_usaf_station_by_zipcode(zipcode):
    usaf = zipcode_usaf.get(zipcode, None)
    return usaf
