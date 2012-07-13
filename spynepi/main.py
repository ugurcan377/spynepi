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

#
# Copyright © Burak Arslan <burak at arskom dot com dot tr>,
#             Arskom Ltd. http://www.arskom.com.tr
# All rights reserved.
#
# Originally retrieved from: https://github.com/arskom/spyne/blob/31ed2c53370a43ad06a4e8cbff392b4b90359b1f/examples/user_manager/server_sqlalchemy.py
#

import logging
logger = logging.getLogger(__name__)

import sqlalchemy

from lxml import etree

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import MetaData
from sqlalchemy import Column

from spyne.application import Application
from spyne.decorator import rpc
from spyne.interface.wsdl import Wsdl11
from spyne.protocol.soap import Soap11
from spyne.model.complex import Iterable
from spyne.model.primitive import Integer
from spyne.model.table import TableModel
from spyne.server.wsgi import WsgiApplication
from spyne.service import ServiceBase
from spyne.protocol.http import HttpRpc
from spyne.protocol.http import SpynePiHttpRpc
from spyne.protocol.xml import XmlObject
from spyne.const.http import HTTP_404

from spynepi.entity.project import RdfService
from spynepi.entity.root import RootService

_user_database = create_engine('sqlite:///:memory:')
metadata = MetaData(bind=_user_database)
DeclarativeBase = declarative_base(metadata=metadata)
Session = sessionmaker(bind=_user_database)

#
# WARNING: You should NOT confuse sqlalchemy types with spyne types. Whenever
# you see an spyne service not starting due to some problem with __type_name__
# that's probably because you did not use an spyne type where you had to (e.g.
# inside @rpc decorator)
#


class User(TableModel, DeclarativeBase):
    __namespace__ = 'spyne.examples.user_manager'
    __tablename__ = 'spyne_user'

    user_id = Column(sqlalchemy.Integer, primary_key=True)
    user_name = Column(sqlalchemy.String(256))
    first_name = Column(sqlalchemy.String(256))
    last_name = Column(sqlalchemy.String(256))


# this is the same as the above user object. Use this method of declaring
# objects for tables that have to be defined elsewhere.
class AlternativeUser(TableModel, DeclarativeBase):
    __namespace__ = 'spyne.examples.user_manager'
    __table__ = User.__table__


class UserManagerService(ServiceBase):
    @rpc(User, _returns=Integer)
    def add_user(ctx, user):
        ctx.udc.session.add(user)
        ctx.udc.session.flush()
        return user.user_id

    @rpc(Integer, _returns=User)
    def get_user(ctx, user_id):
        retval = ctx.udc.session.query(User).filter_by(user_id=user_id).one()
        ctx.udc.session.expunge(retval)
        return retval

    @rpc(User)
    def set_user(ctx, user):
        ctx.udc.session.merge(user)

    @rpc(Integer)
    def del_user(ctx, user_id):
        ctx.udc.session.query(User).filter_by(user_id=user_id).delete()

    @rpc(_returns=Iterable(AlternativeUser))
    def get_all_user(ctx):
        return ctx.udc.session.query(User)


class UserDefinedContext(object):
    def __init__(self):
        self.session = Session()


def _on_method_call(ctx):
    ctx.udc = UserDefinedContext()
    
def _on_method_return_object(ctx):
    ctx.udc.session.commit()
    ctx.udc.session.close()

def main():
    # configure logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.DEBUG)

    # configure application
    #application = Application([UserManagerService], 'spyne.examples.user_manager',
    #            interface=Wsdl11(), in_protocol=Soap11(), out_protocol=Soap11())
    application = Application([RdfService,RootService],"http://usefulinc.com/ns/doap#",
                                in_protocol=SpynePiHttpRpc(), out_protocol=XmlObject())

    application.event_manager.add_listener('method_call', _on_method_call)
    application.event_manager.add_listener('method_return_object', _on_method_return_object)
    
    # configure database
    metadata.create_all()

    # configure server
    try:
        from wsgiref.simple_server import make_server
    except ImportError:
        print "Error: example server code requires Python >= 2.5"

    wsgi_app = WsgiApplication(application)
    server = make_server('127.0.0.1', 7789, wsgi_app)

    # start server
    logger.info("listening to http://127.0.0.1:7789")
    logger.info("wsdl is at: http://localhost:7789/?wsdl")
    server.serve_forever()
