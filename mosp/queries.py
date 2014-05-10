from .models import *

from sqlalchemy import func

from sqlalchemy.exc import DBAPIError

def get_locations():
    try:
        locations = DBSession.query(
                                Location.name,
                            ).all()
    except DBAPIError:
        return HTTPNotFound()

    return locations

def get_location(name):
    try:
        location = DBSession.query(
                                Location.latitude,
                                Location.longitude,
                            ).filter(
                                func.lower(Location.name) ==
                                func.lower(name)
                            ).first()

    except DBAPIError:
        return HTTPNotFound()

    return location
