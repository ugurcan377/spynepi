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

import sys
import logging
logger = logging.getLogger(__name__)

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from spyne.application import Application
from spyne.protocol.xml import XmlObject
from spyne.protocol.html import HtmlTable
from spyne.server.wsgi import WsgiApplication

from spynepi.const import DB_CONNECTION_STRING
from spynepi.const import HOST
from spynepi.const import PORT
from spynepi.db import init_database
from spynepi.protocol import HttpRpc
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


def TWsgiApplication(url_map):
    def _application(environ, start_response, wsgi_url=None):
        urls = url_map.bind_to_environ(environ)
        try:
            endpoint, args = urls.match()
        except HTTPException, e:
            return e(environ, start_response)

        return endpoint(environ, start_response, wsgi_url)

    return _application

def main(connection_string=DB_CONNECTION_STRING):
    # configure logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
#    logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.DEBUG)

    index_app = Application([RootService,IndexService],"http://usefulinc.com/ns/doap#",
                                in_protocol=HttpRpc(), out_protocol=HtmlTable())
    rdf_app = Application([RdfService],"http://usefulinc.com/ns/doap#",
                                in_protocol=HttpRpc(), out_protocol=XmlObject())
    html_app = Application([HtmlService],"http://usefulinc.com/ns/doap#",
                                in_protocol=HttpRpc(), out_protocol=HttpRpc())

    db_handle = init_database(connection_string)

    class UserDefinedContext(object):
        def __init__(self):
            self.session = db_handle.Session()


    def _on_method_call(ctx):
        ctx.udc = UserDefinedContext()


    def _on_method_return_object(ctx):
        ctx.udc.session.commit()
        ctx.udc.session.close()

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

    resource = WSGIResource(reactor, reactor, TWsgiApplication(url_map))
    site = Site(resource)

    reactor.listenTCP(PORT, site)

    logging.info('listening on: %s:%d' % (HOST, PORT))
    logging.info('wsdl is at: http://%s:%d/?wsdl' % (HOST, PORT))

    sys.exit(reactor.run())
