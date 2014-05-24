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
