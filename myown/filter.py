import numpy as np


def create_filter_where(filter):
    filter_where = ""
    if 'earthquake' in filter:
        filter_where = filter_where + \
            f" AND earthquake = {filter['earthquake']}"

    if 'heat_wave' in filter:
        filter_where = filter_where + f" AND heat_wave = {filter['heat_wave']}"

    if 'hail' in filter:
        filter_where = filter_where + f" AND hail = {filter['hail']}"

    if 'tornado' in filter:
        filter_where = filter_where + f" AND tornado = {filter['tornado']}"

    if 'countries' in filter:
        countries = filter["countries"]

        if len(countries) > 0:
            country_join = "' , '".join(countries)
            filter_where = filter_where + f" AND CountryCode IN ('{country_join}')"

    if 'buildings' in filter:
        buildings = filter["buildings"]

        if len(buildings) > 0:
            buildings_join = "' , '".join(buildings)
            filter_where = filter_where + f" AND Building_Type IN ('{buildings_join}')"

    if 'polygons' in filter:
        polygons = filter["polygons"]

        if len(polygons) > 0:
            subs = []
            for polygon in polygons:
                sub_query = f"  ST_CONTAINS(ST_GeomFromText('{polygon}'), ST_Point(Longitude, Latitude)) "
                # sub_query = f"  ST_CONTAINS(ST_GeomFromText('{polygon}', 4326), coor) "
                subs.append(sub_query)

            join = " OR ".join(subs)
            filter_where = f"{filter_where} AND ({join})"

    return filter_where
