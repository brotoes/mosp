from sqlalchemy import (
    Column,
    Index,
    Integer,
    Float,
    Text,
    String,
    CHAR,
    Date,
    DateTime,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Location(Base):
    __tablename__ = 'locations'
    name = Column(CHAR(80), primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

class Gauge(Base):
    __tablename__ = 'gauges'
    gauge_id = Column(Integer, primary_key=True, autoincrement=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(CHAR(80), ForeignKey('locations.name'),
                      primary_key=True, nullable=False)
    quadrant = Column(CHAR(2), ForeignKey('quadrants.name'), nullable=False)
    
    def __init__(self, gauge_id, latitude, longitude, location, quadrant):
        self.gauge_id = gauge_id
        self.latitude = latitude
        self.longitude = longitude
        self.location = location
        self.quadrant = quadrant


class RainReading(Base):
    __tablename__ = 'rain_readings'
    gauge_id = Column(Integer, ForeignKey('gauges.gauge_id'), primary_key=True)
    location = Column(CHAR(80), ForeignKey('gauges.location'), primary_key=True)
    date = Column(Date, primary_key=True)
    amount = Column(Integer, nullable=False)
    
    def __init__(self, gauge_id, location, date, amount):
        self.gauge_id = gauge_id
        self.location = location
        self.date = date
        self.amount = amount


class Region(Base):
    __tablename__ = 'regions'
    name = Column(CHAR(24), primary_key=True)
    quadrant = Column(CHAR(2), ForeignKey('quadrants.name'), nullable=False)
    location = Column(CHAR(80), ForeignKey('quadrants.location'), nullable=False)

    def __init__(self, name, quadrant, location):
        self.name = name
        self.quadrant = quadrant
        self.location = location

class Trap(Base):
    __tablename__ = 'traps'
    date = Column(Date, primary_key=True)
    region = Column(CHAR(24), ForeignKey('regions.name'), primary_key=True)
    count = Column(Integer, nullable=False)

    def __init__(self, date, region, count):
        self.date = date
        self.region = region
        self.count = count

class Quadrant(Base):
    __tablename__ = 'quadrants'
    name = Column(CHAR(2), primary_key=True)
    location = Column(CHAR(80), ForeignKey('locations.name'), primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    def __init__(self, name, location, latitude, longitude):
        self.name = name
        self.location = location
        self.latitude = latitude
        self.longitude = longitude

class Forecast(Base):
    __tablename__ = 'forecasts'
    location = Column(CHAR(80), ForeignKey('locations.name'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    chance = Column(Float, nullable=False)

    def __init__(self, location, date, chance):
        self.location = location
        self.date = date
        self.chance = chance
                      
