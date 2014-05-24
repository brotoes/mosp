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

import transaction
import ast

from .models import *

from sqlalchemy import func

from sqlalchemy.exc import(
                    DBAPIError,
                    IntegrityError,
                          )

"""
returns list of all valid dates for location
"""
def get_dates(location):
    trap = get_trapDates(location)
    rain = get_rainDates(location)
    return sorted(trap + rain)

"""
returns a list of valid dates for trap data
"""
def get_trapDates(location):
    try:
        dates = DBSession.query(
                    Trap.date,
                ).join(
                    Region,
                ).filter(
                    Region.name==Trap.region,
                    func.lower(Region.location)==func.lower(location),
                ).distinct().all()
    except DBAPIError as e:
        print e
        return []

    dates = [str(i[0]) for i in dates]

    return dates

"""
returns a list of valid dates for rain data
"""
def get_rainDates(location):
    try:
        dates = DBSession.query(
                    RainReading.date,
                ).filter(
                    func.lower(RainReading.location)==func.lower(location),
                ).distinct().all()
    except DBAPIError as e:
        print e
        return []

    dates = [str(i[0]) for i in dates]

    return dates

"""
returns timeline of mosquito trap data between start and end dates
Data is returned as a dictionary whose keys are quadrant names. Each key
corresponds to a list of tuples of the form:
(date, count)
where count is the average number of mosquitos found in traps of their quadrant
"""
def get_trapData(start_date, end_date, location):
    data = {}
    try:
        quadrants = DBSession.query(
                                Quadrant.name
                            ).filter(
                                func.lower(Quadrant.location)==func.lower(location)
                            ).all()

        quadrants = [i[0] for i in quadrants]
        for i in quadrants:
            regions = DBSession.query(
                                Region.name
                            ).filter(
                                func.lower(Region.location)==func.lower(location),
                                func.lower(Region.quadrant)==func.lower(i),
                            )
            traps = DBSession.query(
                                Trap.date,
                                func.avg(Trap.count),
                            ).filter(
                                Trap.date.between(start_date, end_date),
                                Trap.region.in_(regions)
                            ).group_by(Trap.date).all()

            data[i] = [[str(j[0]), int(j[1])] for j in traps]
    except DBAPIError as e:
        print e
        return {}

    return data

"""
returns timeline of rainfall data between start and end dates.
Data is returned as a dictionary whose keys are quadrant names. Each key
corresponds to a list of tuples of the form:
(date, amount)
where amount is the average rainfall for gauges of their quadrant
"""
def get_rainData(start_date, end_date, location):
    data = {}
    try:
        readings = DBSession.query(
                                Gauge.quadrant,
                                RainReading.date,
                                func.avg(RainReading.amount),
                            ).filter(
                                Gauge.gauge_id==RainReading.gauge_id,
                                func.lower(Gauge.location)==func.lower(location),
                                func.lower(RainReading.location)==
                                    func.lower(location),
                                RainReading.date.between(start_date, end_date),
                            ).group_by(
                                Gauge.quadrant,
                                RainReading.date,
                            ).all()
    except DBAPIError as e:
        print e
        return {}

    for i in readings:
        new_item = [str(i[1]), int(i[2])]
        if i[0] in data:
            data[i[0]].append(new_item)
        else:
            data[i[0]] = [new_item]

    return data

"""
Returns all-time maximum mosquito count for all traps in location
"""
def get_maxTrap(location):
    try:
        region_max = DBSession.query(
                                Trap.region.label('r'),
                                func.max(Trap.count).label('c'),
                            ).group_by(Trap.region).subquery()
        max_count = DBSession.query(
                                Region.quadrant,
                                func.avg(region_max.c.c),
                            ).filter(
                                Region.name==region_max.c.r,
                                func.lower(Region.location)==func.lower(location),
                            ).group_by(
                                Region.quadrant
                            ).all()
                            
        max_count = [int(i[1]) for i in max_count]

    except DBAPIError as e:
        print e
        return 0

    return max(max_count)

"""
Returns all-time maximum rainfall for all gauges in location
"""
def get_maxRain(location):
    try:
        max_count = DBSession.query(
                            func.max(RainReading.amount)
                        ).filter(
                            func.lower(RainReading.location)==func.lower(location),
                        ).first()
        max_count = int(max_count[0])
    except DBAPIError as e:
        print e
        return 0

    return max_count
"""
Returns all-time average rainfall for each quadrant in location
"""
def get_quadAvgRainfall(location):
    try:
        counts = DBSession.query(
                            Gauge.quadrant,
                            func.avg(RainReading.amount),
                        ).filter(
                            Gauge.gauge_id==RainReading.gauge_id
                        ).group_by(Gauge.quadrant).all()
    except DBAPIError as e:
        print e
        return []

    count_dict = {}

    for i in counts:
        count_dict[i[0]] = float(i[1])

    return count_dict

"""
Return average rainfall for all gauges
"""
def get_avgAmount():
    try:
        readings = DBSession.query(
                                RainReading.gauge_id,
                                func.avg(RainReading.amount),
                            ).group_by(RainReading.gauge_id)
    except DBAPIError as e:
        print e
        return []

    readings = [[int(i[0]), float(i[1])] for i in readings]

    return readings

"""
returns most recent mosquito counts for all quadrants in an area before date
"""
def get_recentTrapCount(location, date):
    try:
        dates = DBSession.query(
                    func.max(Trap.date).label('date'),
                    Region.quadrant.label('quad'),
                    Region.name.label('region'),
                ).filter(
                    Region.name==Trap.region,
                    Trap.date <= date,
                    func.lower(Region.location)==func.lower(location),
                ).group_by(Trap.region).subquery()
        
        counts = DBSession.query(
                    dates.c.date,
                    dates.c.quad,
                    Trap.count,
                ).filter(
                    Region.name==Trap.region,
                    Trap.date==dates.c.date,
                    Trap.region==dates.c.region,
                ).all()
    except DBAPIError as e:
        print e
        return []

    counts = [[str(i[0]), str(i[1]), int(i[2])] for i in counts]

    return counts

"""
returns rainfall of all gauges in a location, nearest before (or on)
the given date
"""
def get_recentRainfall(location, date):
    try:
        dates = DBSession.query(
                    RainReading.gauge_id,
                    func.max(RainReading.date),
                    RainReading.amount,
                ).filter(
                    func.lower(RainReading.location)==func.lower(location),
                    RainReading.date <= date
                ).group_by(RainReading.gauge_id).all()
                    
    except DBAPIError as e:
        print e
        return []

    dates = [[int(i[0]), str(i[1]), int(i[2])] for i in dates]

    return dates

"""
Return all gauges' information in location
"""
def get_gauges(location):
    try:
        gauges = DBSession.query(
                                Gauge.gauge_id,
                                Gauge.latitude,
                                Gauge.longitude,
                                Gauge.location,
                                Gauge.quadrant,
                            ).filter(
                                func.lower(Gauge.location)==
                                func.lower(location)
                            ).all()
    except DBAPIError as e:
        print e
        return []

    gauges = [[int(i[0]), i[1], i[2], i[3], i[4]] for i in gauges]

    return gauges

"""
Return list of all valid location names
"""
def get_locations():
    try:
        locations = DBSession.query(
                                Location.name,
                            ).all()
    except DBAPIError as e:
        print e
        return HTTPNotFound()

    return locations

"""
Return coordinates cooresponding to location names
"""
def get_location(name):
    try:
        location = DBSession.query(
                                Location.latitude,
                                Location.longitude,
                            ).filter(
                                func.lower(Location.name) ==
                                func.lower(name)
                            ).first()

    except DBAPIError as e:
        print e
        return HTTPNotFound()

    return location

"""
Return list of quadrants and their coordinates
"""
def get_quadbounds(location):
    try:
        quads = DBSession.query(
                                Quadrant.latitude,
                                Quadrant.longitude,
                                Quadrant.name,
                            ).filter(
                                func.lower(Quadrant.location)==
                                    func.lower(location)
                            ).all()
        center = DBSession.query(
                                Location.latitude,
                                Location.longitude,
                            ).filter(
                                func.lower(location)==
                                    func.lower(Location.name),
                            ).first()
    except DBAPIError as e:
        print e
        return []
    
    bounds = []

    for i in quads:
        if i[1] <= center[1]:
            bounds.append([i[0], i[1], center[0], center[1], i[2]])
        else:
            bounds.append([center[0], center[1], i[0], i[1], i[2]])

    return bounds

"""
Takes a tuple, data, of the form:
    (Year, Month, Day, gauge_id, quadrant, amount, latitude, longitude)
And inserts in into database. If and entry corresponding to gauge_id does not
exist, it will be created. other wise, only the measurement info will be 
inserted into the database.
"""
def add_reading(data):
    month = {
        'January':1,
        'February':2,
        'March':3,
        'April':4,
        'May':5,
        'June':6,
        'July':7,
        'August':8,
        'September':9,
        'October':10,
        'November':11,
        'December':12,
            }
    date = str(data[0]) + '-' + str(month[data[1]]) + '-' + str(data[2])
    date = date.strip()

    gauge_id = data[3][1:].strip()
    gauge_id = int(gauge_id)

    quadrant = data[4].strip()

    amount = int(data[5])

    latitude = ast.literal_eval(data[6])
    longitude = ast.literal_eval(data[7])
    
    try:
        with transaction.manager:
            #Try to add measurement to database
            reading = RainReading(gauge_id, 'Edmonton', date, amount)
            DBSession.add(reading)
    except IntegrityError:
        with transaction.manager:
            gauge = Gauge(gauge_id, latitude, longitude, 'Edmonton', quadrant)
            DBSession.add(gauge)
        with transaction.manager:
            #retry measurement insertion
            reading = RainReading(gauge_id, 'Edmonton', date, amount)
            DBSession.add(reading)

"""
inserts trap data into traps table
"""
def add_trap(counts, raw_date):
    regions = ['rural northwest', 'rural northeast', 'rural southeast',
               'rivervalley east', 'rivervalley west', 'residential north',
               'rural southwest', 'lagoon', 'residential south']
    date = raw_date[:10]
    
    for i in range(len(counts)):
        count = int(counts[i] or 0)
        region = regions[i]
    
        with transaction.manager:
            trap = Trap(date, region, count)
            DBSession.add(trap)
