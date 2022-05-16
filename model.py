from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import config as cfg

Base = declarative_base()
Base.metadata.schema = 'ysql_idiversity'

class Organization(Base):
    __tablename__ = 'organization'
    __table_args__ = {"schema": "{0}".format(cfg.schema)}

    org_id = Column(Integer, primary_key=True)
    name = Column(String)
    about = Column(String)
    industry = Column(String)
    raw = Column(JSON)
    address = relationship('Address', foreign_keys=[org_id], primaryjoin='Address.org_id == Organization.org_id',
                           back_populates='organization',
                           uselist=False)
    people = relationship('People', foreign_keys=[org_id], primaryjoin='People.org_id == Organization.org_id',
                          uselist=True)

    def __repr__(self):
        return "<Organization(org_id=%s name='%s', industry='%s')>" % \
               (self.org_id, self.name, self.industry)

    def to_json(self):
        organization_json = {
            "org_id": self.org_id,
            "name": self.name,
            "about": self.about,
            "industry": self.industry,
            "address": self.address.to_json(),
            "raw": self.raw
        }

        organization_json['people'] = [
            line.to_json() for line in self.people
        ]

        return organization_json


class Address(Base):
    __tablename__ = "address"
    __table_args__ = {"schema": "{0}".format(cfg.schema)}

    address_id = Column(Integer, primary_key=True)
    address_line1 = Column(String)
    address_line2 = Column(String)
    address_line3 = Column(String)
    city = Column(String)
    state = Column(String)
    pincode = Column(String)
    country = Column(String)
    org_id = Column(Integer)

    organization = relationship('Organization', foreign_keys=[org_id],
                                primaryjoin='Address.org_id == Organization.org_id',
                                uselist=False)

    def __repr__(self):
        return "<Address(address_id=%s address_line1=%s address_line2: %s city=%s state=%s pincode: %s country=%s org_id: %s)>" % \
               (self.address_id, self.address_line1, self.address_line2, self.city, self.state,
                self.pincode,
                self.country, self.org_id)

    def to_json(self):
        address_json = {
            "address_id": self.address_id,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "address_line3": self.address_line3,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
            "country": self.country,
            "org_id": self.org_id
        }

        return address_json


class People(Base):
    __tablename__ = "people"
    __table_args__ = {"schema": "{0}".format(cfg.schema)}

    people_id = Column(Integer, primary_key=True)
    name = Column(String)
    position = Column(String)
    department = Column(String)
    org_id = Column(Integer)
    organization = relationship("Organization", foreign_keys=[org_id],
                                primaryjoin='People.org_id == Organization.org_id')

    def __repr__(self):
        return "<People(people_id=%s, name=%s, position=%s, department=%s)>" % \
               (self.people_id, self.name, self.position, self.department)

    def to_json(self):
        return {
            "people_id": self.people_id,
            "name": self.name,
            "position": self.position,
            "department": self.department,
            "org_id": self.org_id
        }
