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

import open_data

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

    location = get_location(city)

    if location == HTTPNotFound():
        return location
    elif location == None:
        return HTTPNotFound()

    return {
            'api_key':api_key,
            'latitude':location[0],
            'longitude':location[1],
            }

@view_config(route_name='refresh')
def refresh(request):
    

    return {}

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

