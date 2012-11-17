
from collections import namedtuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spyne.model.complex import table
from spyne.model.complex import Array
from spyne.model.complex import TTableModel
from spyne.model.primitive import Date
from spyne.model.primitive import Integer32
from spyne.model.primitive import String
from spyne.model.primitive import Unicode

from spynepi.const import TABLE_PREFIX

DatabaseHandle = namedtuple("DatabaseHandle", ["db", "Session"])
TableModel = TTableModel()


class Person(TableModel):
    __tablename__ = "%s_person"  % TABLE_PREFIX
    __table_args__ = {"sqlite_autoincrement": True}

    id = Integer32(primary_key=True)
    person_name = String(60)
    person_email = String(60)


class Distribution(TableModel):
    __tablename__ = "%s_distribution"  % TABLE_PREFIX
    __table_args__ = {"sqlite_autoincrement": True}

    id = Integer32(primary_key=True)

    # TO-DO Add Content data
    content_name = String(256)
    content_path = String(256)
    dist_download_url = String(256)
    dist_comment = String(256)
    dist_file_type = String(256)
    dist_md5 = String(256)
    py_version = String(10)
    protocol_version = String(10)


class Release(TableModel):
    __tablename__ = "%s_release"  % TABLE_PREFIX
    __table_args__ = {"sqlite_autoincrement": True}

    id = Integer32(primary_key=True)
    release_cdate = Date
    rdf_about = String(256)
    release_version = String(10)
    meta_version = String(10)
    release_summary = String(256)
    release_platform = String(30)

    distributions = Array(Distribution).store_as(table(right="release_id"))


class Package(TableModel):
    __tablename__ = "%s_package"  % TABLE_PREFIX
    __table_args__ = {"sqlite_autoincrement": True}

    id = Integer32(primary_key=True)
    package_name = String(40)
    package_cdate = Date
    package_description = Unicode
    rdf_about = Unicode(256)
    package_license = Unicode(40)
    package_home_page = String(256)

    owners = Array(Person).store_as(table(right="owner_id"))
    releases = Array(Release).store_as(table(right="package_id"))


def init_database(connection_string):
    db = create_engine(connection_string)

    TableModel.Attributes.sqla_metadata.bind = db
    Session = sessionmaker(bind=db)

    # So that metadata gets updated with table names.
    import spynepi.entity.root
    import spynepi.entity.project

    TableModel.Attributes.sqla_metadata.create_all(checkfirst=True)

    return DatabaseHandle(db=db, Session=Session)
