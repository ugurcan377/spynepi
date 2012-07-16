# encoding: utf8
#
# (C) Copyright Arskom Ltd. <info@arskom.com.tr>
#               Uğurcan Ergün <ugurcanergn@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#

import datetime
import os

import logging
logger = logging.getLogger(__name__)

import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

from sqlalchemy import MetaData
from sqlalchemy import Column

from spyne.decorator import rpc
from spyne.model.table import TableModel
from spyne.model.primitive import String
from spyne.model.primitive import Unicode
from spyne.model.binary import File
from spyne.service import ServiceBase

from spynepi.const import TABLE_PREFIX

_user_database = create_engine('postgresql://ugurcan:Arskom1986@localhost:5432/test')
metadata = MetaData(bind=_user_database)
DeclarativeBase = declarative_base(metadata=metadata)
Session = sessionmaker(bind=_user_database)

class Package(TableModel, DeclarativeBase):
    __tablename__ = "%s_package"  % TABLE_PREFIX

    id = Column(sqlalchemy.Integer, primary_key=True)
    package_name = Column(sqlalchemy.String(40))
    package_cdate = Column(sqlalchemy.Date)
    rdf_about = Column(sqlalchemy.String(256))
    owners = relationship("Person", backref="%s_package" % TABLE_PREFIX)
    package_license = Column(sqlalchemy.String(40))
    package_home_page = Column(sqlalchemy.String(256))
    releases = relationship("Release", backref="%s_package" % TABLE_PREFIX)


class Person(TableModel, DeclarativeBase):
    __tablename__ = "%s_person"  % TABLE_PREFIX

    id = Column(sqlalchemy.Integer, primary_key=True)
    person_name = Column(sqlalchemy.String(60))
    person_email = Column(sqlalchemy.String(60))
    package_id = Column(sqlalchemy.Integer, ForeignKey("%s_package.id" % TABLE_PREFIX))


class Release(TableModel, DeclarativeBase):
    __tablename__ = "%s_release"  % TABLE_PREFIX

    id = Column(sqlalchemy.Integer, primary_key=True)
    package_id = Column(sqlalchemy.Integer, ForeignKey("%s_package.id" % TABLE_PREFIX))
    rdf_about = Column(sqlalchemy.String(256))
    release_version = Column(sqlalchemy.String(10))
    release_description = Column(sqlalchemy.String(256))
    meta_version = Column(sqlalchemy.String(10))
    release_platform = Column(sqlalchemy.String(30))
    distributions = relationship("Distribution", backref="%s_release" % TABLE_PREFIX)


class Distribution(TableModel, DeclarativeBase):
    __tablename__ = "%s_distribution"  % TABLE_PREFIX

    id = Column(sqlalchemy.Integer, primary_key=True)
    release_id = Column(sqlalchemy.Integer, ForeignKey("%s_release.id" % TABLE_PREFIX))
    # TO-DO Add Content data
    content_name = Column(sqlalchemy.String(256))
    content_path = Column(sqlalchemy.String(256))
    dist_download_url = Column(sqlalchemy.String(256))
    dist_comment = Column(sqlalchemy.String(256))
    dist_file_type = Column(sqlalchemy.String(256))
    dist_md5 = Column(sqlalchemy.String(60))
    py_version = Column(sqlalchemy.String(10))
    dist_summary = Column(sqlalchemy.String(256))
    protocol_version = Column(sqlalchemy.String(10))


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
