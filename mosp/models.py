from sqlalchemy import (
    Column,
    Index,
    Integer,
    Float,
    Text,
    String,
    CHAR,
    Date,
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
    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)

    def __init__(self, name, lat, long):
        self.name = name
        self.lat = lat
        self.long = long

class Gauge(Base):
    __tablename__ = 'gauges'
    gauge_id = Column(Integer, primary_key=True)
    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)
    quadrant = Column(CHAR(2), nullable=False)
    
    def __init__(self, gauge_id, lat, long, quadrant):
        self.gauge_id = gauge_id
        self.lat = lat
        self.long = long
        self.quadrant = quadrant


class RainReading(Base):
    __tablename__ = 'rain_readings'
    gauge_id = Column(Integer, ForeignKey('gauges.gauge_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    
    def __init__(self, gauge_id, date):
        self.gauge_id = gauge_id
        self.date = date


class Region(Base):
    __tablename__ = 'regions'
    name = Column(String(24), primary_key=True)
    quadrant = Column(CHAR(2), nullable=False)

    def __init__(self, name, quadrant):
        self.name = name
        self.quadrant = quadrant
