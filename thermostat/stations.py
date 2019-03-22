import logging
from eeweather import (
        zcta_to_lat_long,
        rank_stations,
        select_station)

logging.getLogger(__name__)


def lookup_station_by_zipcode(zipcode):
    """ Look up the station by zipcode from eeweather
    :zipcode:  String
    :returns:  Station

    """
    try:
        lat, lon = zcta_to_lat_long(zipcode)
        station_ranking = rank_stations(lat, lon)
        station, warnings = select_station(station_ranking)
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
            # return None

        return str(station)
    except Exception:
        return None
