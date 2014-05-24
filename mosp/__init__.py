from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

import ConfigParser
import os


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    #Parse database and gmap api keys
    sqlalchemy_url = settings['sqlalchemy.url'].split(':')
    if (sqlalchemy_url[0].strip() == 'file'):
        parser = ConfigParser.ConfigParser()
        parser.readfp(open(os.path.expanduser(sqlalchemy_url[1].strip()[2:])))
        settings['sqlalchemy.url'] = parser.get('main', 'db.url')
    gmap_key = settings['gmapv3'].split(':')
    if (gmap_key[0].strip() == 'file'):
        parser = ConfigParser.ConfigParser()
        parser.readfp(open(os.path.expanduser(gmap_key[1].strip()[2:])))
        settings['gmapv3'] = parser.get('main', 'gmapv3')
    
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('map', '/location/{city}')
    config.add_route('refresh', '/refresh')
    config.add_route('dates', '/dates/{location}/{type}')
    config.add_route('rainfall', '/rainfall/{city}/{date}')
    config.add_route('traps', '/traps/{city}/{date}')

    config.scan()
    return config.make_wsgi_app()
