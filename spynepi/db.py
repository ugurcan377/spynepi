
from collections import namedtuple

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DatabaseHandle = namedtuple("DatabaseHandle", ["db", "Session"])
metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)

def init_database(connection_string):
    db = create_engine(connection_string)

    metadata.bind = db
    Session = sessionmaker(bind=db)

    return DatabaseHandle(db=db, Session=Session)
