from spynepi.main import __tablename__
import logging
logger = logging.getLogger(__name__)

import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

    package_id = Column(sqlalchemy.Integer, primary_key = True)
    package_name = Column(sqlalchemy.String(40))
    package_cdate = Column(sqlalchemy.DateTime)
    owners = Column()
    license = Column(sqlalchemy.String(40))
    home_page = Column(sqlalchemy.String(256))
    releases = Column()

class Person(TableModel,DeclarativeBase):
    __tablename__ = "Person"

    person_id = Column(sqlalchemy.Integer, primary_key = True)
    person_name = Column(sqlalchemy.String(60))
    person_email = Column(sqlalchemy.String(60))

class Release(TableModel,DeclarativeBase):
    __tablename__ = "Release"

    release_id = Column(sqlalchemy.Integer, primary_key = True)
    package = Column()
    path = Column(sqlalchemy.String(256))
    version = Column(sqlalchemy.Float)
    description = Column(sqlalchemy.String(256))
    meta_version = Column(sqlalchemy.Float)
    platform = Column(sqlalchemy.String(20))
    distribution = Column()

class Distribution(TableModel,DeclarativeBase):
    __tablename__ = "Distribution"

    dist_id = Column(sqlalchemy.Integer, primary_key = True)
    release = Column()
    content = Column()
    download_url = Column(sqlalchemy)
    comment = Column(sqlalchemy.String(256))
    file_type = Column()
    md5 = Column(sqlalchemy.String(60))
    py_version= Column(sqlalchemy.Float)
    summary = Column(sqlalchemy.String(256))
    protocol_version = Column(sqlalchemy.Float)


class SomeService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, Unicode, File)
    def register(name, license, author, home_page, content):
        print "\n\n\n\nHEY:", name, license, author, home_page, content
