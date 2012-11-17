
from collections import namedtuple

from sqlalchemy import create_engine
from spyne.model.complex import TTableModel
from sqlalchemy.orm import sessionmaker

DatabaseHandle = namedtuple("DatabaseHandle", ["db", "Session"])
TableModel = TTableModel()


def init_database(connection_string):
    db = create_engine(connection_string)

    TableModel.Attributes.sqla_metadata.bind = db
    Session = sessionmaker(bind=db)

    # So that metadata gets updated with table names.
    import spynepi.entity.root
    import spynepi.entity.project

    TableModel.Attributes.sqla_metadata.create_all(checkfirst=True)

    return DatabaseHandle(db=db, Session=Session)
