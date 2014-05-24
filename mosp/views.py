###############################################################################
#Copyright 2014 CHOICE Online Marketing Group
#
#This file is part of MosP.
#
#MosP is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#MosP is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with MosP.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

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

@view_config(route_name='dates', renderer='json')
def dates(request):
    date_type = request.matchdict['type']
    location = request.matchdict['location']
    dates = []

    if date_type == 'rain':
        dates = get_rainDates(location)
    elif date_type == 'trap':
        dates = get_trapDates(location)

    return dates

@view_config(route_name='rainfall', renderer='json')
def rainfall(request):
    city = request.matchdict['city']
    date = request.matchdict['date']

    return {'data':get_recentRainfall(city, date)}

@view_config(route_name='traps', renderer='json')
def traps(request):
    city = request.matchdict['city']
    date = request.matchdict['date']

    return {'data':get_recentTrapCount(city, date)}

@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    #TODO get list of cities and return links
    locations = get_locations()
    return {'locations': locations}


@view_config(route_name='map', renderer='templates/map.pt')
def map(request):
    api_key = request.registry.settings['gmapv3']
   
    start_date='0000-00-00'
    end_date = '9999-12-21'
    city = request.matchdict['city']
    traps = get_trapData(start_date, end_date, city)
    location = get_location(city)
    quadbounds = get_quadbounds(city)
    gauges = get_gauges(city)
    rain_data = get_rainData(start_date, end_date, city)
    readings = get_avgAmount()
    max_trap = get_maxTrap(city)
    max_rain = get_maxRain(city)
    recent_rainfall = get_recentRainfall(city, end_date)
    recent_trapCount = get_recentTrapCount(city, end_date)
    dates = get_dates(city)

    if quadbounds == HTTPNotFound():
        return quadbounds
    
    if location == HTTPNotFound():
        return location
    elif location == None:
        return HTTPNotFound()

    return {
            'location':city,
            'recent_rainfall':recent_rainfall,
            'recent_trapCount':recent_trapCount,
            'api_key':api_key,
            'center':location,
            'gauges':gauges,
            'readings':readings,
            'quadrants':quadbounds,
            'traps':traps,
            'max_trap':max_trap,
            'max_rain':max_rain,
            'dates':dates,
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

