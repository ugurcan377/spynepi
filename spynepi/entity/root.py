
import datetime
import os

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


class Package(TableModel, DeclarativeBase):
    __tablename__ = "Package"

    id = Column(sqlalchemy.Integer, primary_key=True)
    package_name = Column(sqlalchemy.String(40))
    package_cdate = Column(sqlalchemy.Date)
    rdf_about = Column(sqlalchemy.String(256))
    owners = relationship("Person", backref="Package")
    license = Column(sqlalchemy.String(40))
    home_page = Column(sqlalchemy.String(256))
    releases = relationship("Release", backref="Package")


class Person(TableModel, DeclarativeBase):
    __tablename__ = "Person"

    id = Column(sqlalchemy.Integer, primary_key=True)
    person_name = Column(sqlalchemy.String(60))
    person_email = Column(sqlalchemy.String(60))
    package_id = Column(sqlalchemy.Integer, ForeignKey("Package.id"))


class Release(TableModel, DeclarativeBase):
    __tablename__ = "Release"

    id = Column(sqlalchemy.Integer, primary_key=True)
    package_id = Column(sqlalchemy.Integer, ForeignKey("Package.id"))
    rdf_about = Column(sqlalchemy.String(256))
    version = Column(sqlalchemy.Float)
    description = Column(sqlalchemy.String(256))
    meta_version = Column(sqlalchemy.Float)
    platform = Column(sqlalchemy.String(30))
    distribution = relationship("Distribution", backref="Release")


class Distribution(TableModel, DeclarativeBase):
    __tablename__ = "Distribution"

    id = Column(sqlalchemy.Integer, primary_key=True)
    release_id = Column(sqlalchemy.Integer, ForeignKey("Release.id"))
    # TO-DO Add Content data
    content_name = Column(sqlalchemy.String(256))
    content_path = Column(sqlalchemy.String(256))
    download_url = Column(sqlalchemy.String(256))
    comment = Column(sqlalchemy.String(256))
    file_type = Column(sqlalchemy.String(256))
    md5 = Column(sqlalchemy.String(60))
    py_version = Column(sqlalchemy.Float)
    summary = Column(sqlalchemy.String(256))
    protocol_version = Column(sqlalchemy.Float)


class RootService(ServiceBase):
    @rpc()
    def register(ctx):
        body = ctx.in_body_doc
        #TO-DO Add a method check
        file = ctx.in_body_doc["content"][0]
        f = open("hede.zip","w")#str(os.path.join("/workspace/pypi",
                #str(body["name"][0]),str(body["version"][0]),file.name)),"w")
        for d in file.data:
            f.write(d)
        f.close()
        package = Package(name=str(body["name"][0]),
            package_cdate=datetime.date.today,
            rdf_about = os.path.join("/pypi",str(body["name"][0])),
            license=str(body["license"][0]),
            home_page=str(body["home_page"][0])
        )

        package.owners.append(Person(person_name=str(body["author"][0]),
            person_email=str(body["author_email"][0]),
        )
        )

        package.releases.append(Release(rdf_about=os.path.join("/pypi",
                str(body["name"][0]),str(body["version"][0])),
            version=str(body["version"][0]),
            description=str(body["description"][0]),
            meta_version=str(body["metadata_version"][0]),
            platform=str(body["platform"][0]),
        )
        )
        os.path.join("/pypi",str(body["name"][0]),str(body["version"][0]),file.name)
        package.releases.distribution.append(Distribution(content_name = file.name,
            content_path=os.path.join("/pypi",
                str(body["name"][0]),str(body["version"][0]),file.name),
            download_url=str(body["download_url"][0]),
            comment=str(body["comment"][0]),
            file_type=str(body["filetype"][0]),
            md5=str(body["md5_digest"][0]),
            py_version=str(body["pyversion"][0]),
            summary=str(body["summary"][0]) ,
            protocol_version=str(body["protocol_version"][0]),
        )
        )
