import transaction
import ast

from .models import *

from sqlalchemy import func

from sqlalchemy.exc import(
                    DBAPIError,
                    IntegrityError,
                          )

"""
returns a list of valid dates for trap data
"""
def get_trapDates(location):
    pass

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
        max_count = DBSession.query(
                                func.max(Trap.count)
                            ).join(
                                Region
                            ).filter(
                                func.lower(Region.location)==func.lower(location),
                                Region.name==Trap.region,
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

def get_locations():
    try:
        locations = DBSession.query(
                                Location.name,
                            ).all()
    except DBAPIError as e:
        print e
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

    except DBAPIError as e:
        print e
        return HTTPNotFound()

    return location

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
