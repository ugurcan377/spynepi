
import logging
logger = logging.getLogger(__name__)

import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref

from sqlalchemy import MetaData
from sqlalchemy import Column

from spyne.decorator import rpc
from spyne.model.table import TableModel
from spyne.model.primitive import String
from spyne.model.primitive import Unicode
from spyne.model.binary import File
from spyne.service import ServiceBase

_user_database = create_engine('sqlite:///:memory:')
metadata = MetaData(bind=_user_database)
DeclarativeBase = declarative_base(metadata=metadata)
Session = sessionmaker(bind=_user_database)

class Package(TableModel,DeclarativeBase):
    __tablename__ = "Package"

    id = Column(sqlalchemy.Integer, primary_key=True)
    package_name = Column(sqlalchemy.String(40))
    package_cdate = Column(sqlalchemy.DateTime)
    owners = relationship("Person", backref="Package")
    license = Column(sqlalchemy.String(40))
    home_page = Column(sqlalchemy.String(256))
    releases = relationship("Release", backref="Package")

class Person(TableModel,DeclarativeBase):
    __tablename__ = "Person"

    id = Column(sqlalchemy.Integer, primary_key=True)
    person_name = Column(sqlalchemy.String(60))
    person_email = Column(sqlalchemy.String(60))
    package_id = Column(sqlalchemy.Integer, ForeignKey("Package.id"))

class Release(TableModel,DeclarativeBase):
    __tablename__ = "Release"

    id = Column(sqlalchemy.Integer, primary_key=True)
    package_id = Column(sqlalchemy.Integer, ForeignKey("Package.id"))
    path = Column(sqlalchemy.String(256))
    version = Column(sqlalchemy.Float)
    description = Column(sqlalchemy.String(256))
    meta_version = Column(sqlalchemy.Float)
    platform = Column(sqlalchemy.String(30))
    distribution = relationship("Distribution", backref="Release")

class Distribution(TableModel,DeclarativeBase):
    __tablename__ = "Distribution"

    id = Column(sqlalchemy.Integer, primary_key = True)
    release_id = Column(sqlalchemy.Integer, ForeignKey("Release.id"))
    # TO-DO Add Content data
    download_url = Column(sqlalchemy.String(256))
    comment = Column(sqlalchemy.String(256))
    file_type = Column(sqlalchemy.String(256))
    md5 = Column(sqlalchemy.String(60))
    py_version= Column(sqlalchemy.Float)
    summary = Column(sqlalchemy.String(256))
    protocol_version = Column(sqlalchemy.Float)


class RootService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, Unicode, File)
    def register(name, license, author, home_page, content):
        print "%s = path \n %s = name" %(str(content.path),str(content.name))
