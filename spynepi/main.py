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

import logging
logger = logging.getLogger(__name__)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import MetaData

from spyne.application import Application
from spyne.server.wsgi import WsgiApplication
from spyne.protocol.xml import XmlObject
from spyne.protocol.html import HtmlTable
from spyne.protocol.html import HtmlPage

from spynepi.protocol import HttpRpc
from spynepi.protocol import SpynePiHttpRpc
from spynepi.entity.html import IndexService
from spynepi.entity.html import HtmlService
from spynepi.entity.project import RdfService
from spynepi.entity.root import RootService
from spynepi.entity.root import Package
from spynepi.entity.root import Person
from spynepi.entity.root import Release
from spynepi.entity.root import Distribution

from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map,Rule
_user_database = create_engine('postgresql://ugurcan:Arskom1986@localhost:5432/test')
metadata = MetaData(bind=_user_database)
DeclarativeBase = declarative_base(metadata=metadata)
Session = sessionmaker(bind=_user_database)


class UserDefinedContext(object):
    def __init__(self):
        self.session = Session()


def _on_method_call(ctx):
    ctx.udc = UserDefinedContext()


def _on_method_return_object(ctx):
    ctx.udc.session.commit()
    ctx.udc.session.close()

def TWsgiApplication(url_map):
    def _application(environ, start_response, wsgi_url=None):
        urls = url_map.bind_to_environ(environ)
        try:
            endpoint, args = urls.match()
        except HTTPException, e:
            return e(environ, start_response)

        return endpoint(environ, start_response, wsgi_url)

    return _application

def main():
    # configure logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.DEBUG)

    index_app = Application([RootService,IndexService],"http://usefulinc.com/ns/doap#",
                                in_protocol=HttpRpc(), out_protocol=HtmlTable())
    rdf_app = Application([RdfService],"http://usefulinc.com/ns/doap#",
                                in_protocol=HttpRpc(), out_protocol=XmlObject())
    html_app = Application([HtmlService],"http://usefulinc.com/ns/doap#",
                                in_protocol=HttpRpc(), out_protocol=HttpRpc())

    index_app.event_manager.add_listener('method_call', _on_method_call)
    index_app.event_manager.add_listener('method_return_object', _on_method_return_object)
    rdf_app.event_manager.add_listener('method_call', _on_method_call)
    rdf_app.event_manager.add_listener('method_return_object', _on_method_return_object)
    html_app.event_manager.add_listener('method_call', _on_method_call)
    html_app.event_manager.add_listener('method_return_object', _on_method_return_object)

    # configure database
    Package.__table__.create(checkfirst=True)
    Person.__table__.create(checkfirst=True)
    Release.__table__.create(checkfirst=True)
    Distribution.__table__.create(checkfirst=True)


    # configure server
    try:
        from wsgiref.simple_server import make_server
    except ImportError:
        print "Error: example server code requires Python >= 2.5"

    wsgi_index = WsgiApplication(index_app)
    wsgi_rdf = WsgiApplication(rdf_app)
    wsgi_html = WsgiApplication(html_app)
    url_map = Map([Rule("/", endpoint=wsgi_index),
        Rule("/<string:project_name>/<string:version>/doap.rdf",endpoint=wsgi_rdf),
        Rule("/<string:project_name>/doap.rdf",endpoint=wsgi_rdf),
        Rule("/<string:project_name>/<string:version>/", endpoint=wsgi_html),
        Rule("/<string:project_name>/<string:version>", endpoint=wsgi_html),
        Rule("/<string:project_name>/", endpoint=wsgi_html),
        Rule("/<string:project_name>", endpoint=wsgi_html),
        Rule("/files/<string:project_name>/<string:version>/<string:download>",
                endpoint=wsgi_html),
        ])

    host = '0.0.0.0'
    server = make_server(host, 7789, TWsgiApplication(url_map))

    # start server
    logger.info("listening to http://%s:7789" % host)
    logger.info("wsdl is at: http://localhost:7789/?wsdl")
    server.serve_forever()
