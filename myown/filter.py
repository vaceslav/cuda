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

    return filter_where
