from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from sqlalchemy import func

from .models import (
    DBSession,
    Location
    )


@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    #TODO get list of cities and return links

    return {}


@view_config(route_name='map', renderer='templates/map.pt')
def map(request):
    api_key = request.registry.settings['gmapv3']

    city = request.matchdict['city']

    location = DBSession.query(
                            Location.lat,
                            Location.long,
                        ).filter(
                            func.lower(Location.name) ==
                            func.lower(city.upper())
                        ).first()

    return {
            'api_key':api_key,
            'latitude':location[0],
            'longitude':location[1],
            }


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

