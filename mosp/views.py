from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from sqlalchemy import func

from queries import *

from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound,
    HTTPNotFound,
    )

from .models import (
    DBSession,
    Location
    )

from open_data import *

@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    #TODO get list of cities and return links
    locations = get_locations()
    print locations
    return {'locations': locations}


@view_config(route_name='map', renderer='templates/map.pt')
def map(request):
    api_key = request.registry.settings['gmapv3']
    
    city = request.matchdict['city']
    traps = get_trapData('0000-00-00', '9999-12-31', city)
    location = get_location(city)
    quadbounds = get_quadbounds(city)
    gauges = get_gauges(city)
    rain_data = get_rainData('0000-00-00', '9999-12-31', city)
    readings = get_avgAmount()

    print get_maxTrap(city)

    if quadbounds == HTTPNotFound():
        return quadbounds
    
    if location == HTTPNotFound():
        return location
    elif location == None:
        return HTTPNotFound()

    return {
            'api_key':api_key,
            'center':location,
            'gauges':gauges,
            'readings':readings,
            'quadrants':quadbounds,
            'traps':traps,
            }

@view_config(route_name='refresh')
def refresh(request):
    #rain meters
    """
    Significant Columns:
     9: Year
    10: Month
    11: Day
    12: ID
    13: Quadrant
    14: Amount (in millimeters)
    15: Latitude
    16: Longitude
    """
    meter_data = OpenData(
                    'https://data.edmonton.ca/api/views/7fus-qa4r/',
                    'rows.json',
                        )
    meter_data.add_get('accessType', 'DOWNLOAD')
    meter_data.refresh()

    for i in meter_data.data['data']:
        add_reading(i[9:17])

    #trap data
    trap_data = OpenData(
                    'https://data.edmonton.ca/api/views/5zeu-wkpv/',
                    'rows.json',
                        )
    trap_data.add_get('accessType', 'DOWNLOAD')
    trap_data.refresh()

    last_date = None
    cur_counts = []
    for i in trap_data.data['data']:
        print "LAST DATE:" + str(last_date)
        print "i[8] (DATE)" + str(i[8])
        if last_date == i[8]:
            cur_counts = [cur_counts[j] + int(i[13:22][j] or 0) for j in range(len(cur_counts))]
        else:
            if last_date != None:
                add_trap(cur_counts, last_date)
            last_date = i[8]
            cur_counts = i[13:22]
            cur_counts = [int(j or 0) for j in cur_counts]

    return Response(trap_data.url)

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_mosp_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

