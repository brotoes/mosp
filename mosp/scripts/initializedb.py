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

import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import *


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    
    #Create data
    location = Location(name='Edmonton',
                        latitude=53.5333,
                        longitude=-113.5000)

    quads = {}
    quads['NW'] = Quadrant(name='NW', location='Edmonton',
                           latitude=53.772321, longitude=-113.823538)
    quads['NE'] = Quadrant(name='NE', location='Edmonton',
                           latitude=53.765016, longitude=-113.180838)
    quads['SE'] = Quadrant(name='SE', location='Edmonton',
                           latitude=53.307971, longitude=-113.242636)
    quads['SW'] = Quadrant(name='SW', location='Edmonton',
                           latitude=53.265281, longitude=-113.925162)

    regions = {}
    regions['rural_nw'] = Region(name='rural northwest', quadrant='NW',
                                 location='Edmonton')
    regions['rural_ne'] = Region(name='rural northeast', quadrant='NE',
                                 location='Edmonton')
    regions['rural_se'] = Region(name='rural southeast', quadrant='SE',
                                 location='Edmonton')
    regions['rural_sw'] = Region(name='rural southwest', quadrant='SW',
                                 location='Edmonton')
    regions['rivervalley_e'] = Region(name='rivervalley east', quadrant='NE',
                                      location='Edmonton')
    regions['rivervalley_w'] = Region(name='rivervalley west', quadrant='SW',
                                      location='Edmonton')
    regions['res_n'] = Region(name='residential north', quadrant = 'NW',
                              location='Edmonton')
    regions['res_s'] = Region(name='residential south', quadrant = 'SE',
                              location='Edmonton')
    regions['lagoon'] = Region(name='lagoon', quadrant='NW',
                               location='Edmonton')

    #Insert data into database
    with transaction.manager:
        DBSession.add(location)

    with transaction.manager:
        for i in quads:
            DBSession.add(quads[i])
    
    with transaction.manager:
        for i in regions:
            DBSession.add(regions[i])
