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

import sys

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from spyne.application import Application
from spyne.protocol.xml import XmlDocument
from spyne.protocol.html import HtmlTable
from spyne.protocol.http import HttpRpc
from spyne.server.wsgi import WsgiApplication

from spynepi.const import DB_CONNECTION_STRING
from spynepi.const import HOST
from spynepi.const import PORT
from spynepi.db import init_database
from spynepi.entity.html import IndexService
from spynepi.entity.html import HtmlService
from spynepi.entity.project import RdfService
from spynepi.entity.root import RootService

from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map
from werkzeug.routing import Rule

from sqlalchemy.orm.exc import NoResultFound
from spyne.error import ResourceNotFoundError


def TWsgiApplication(url_map):
    def _application(environ, start_response, wsgi_url=None):
        urls = url_map.bind_to_environ(environ)
        try:
            endpoint, args = urls.match()
        except HTTPException, e:
            return e(environ, start_response)

        return endpoint(environ, start_response, wsgi_url)

    return _application


class MyApplication(Application):
    def call_wrapper(self, ctx):
        """This is the application-wide exception transforming function."""

        try:
            return Application.call_wrapper(self, ctx)

        except NoResultFound, e:
            ctx.out_string = ["Resource not found"]
            raise ResourceNotFoundError() # Return HTTP 404


def main(connection_string=DB_CONNECTION_STRING):
    # configure logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    #logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.DEBUG)

    index_app = MyApplication([RootService, IndexService],"http://usefulinc.com/ns/doap#",
                                in_protocol=HttpRpc(), out_protocol=HtmlTable())

    rdf_app = MyApplication([RdfService],"http://usefulinc.com/ns/doap#",
                                in_protocol=HttpRpc(), out_protocol=XmlDocument())

    html_app = MyApplication([HtmlService],"http://usefulinc.com/ns/doap#",
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

    wsgi_index = WsgiApplication(index_app)
    wsgi_rdf = WsgiApplication(rdf_app)
    wsgi_html = WsgiApplication(html_app)
    url_map = Map([Rule("/", endpoint=wsgi_index),
        Rule("/<project_name>", endpoint=wsgi_html),
        Rule("/<project_name>/", endpoint=wsgi_html),
        Rule("/<project_name>/doap.rdf",endpoint=wsgi_rdf),
        Rule("/<project_name>/<version>", endpoint=wsgi_html),
        Rule("/<project_name>/<version>/", endpoint=wsgi_html),
        Rule("/<project_name>/<version>/doap.rdf", endpoint=wsgi_rdf),
        Rule("/files/<project_name>/<version>/<download>", endpoint=wsgi_html),
    ])

    resource = WSGIResource(reactor, reactor, TWsgiApplication(url_map))
    site = Site(resource)

    reactor.listenTCP(PORT, site)

    logging.info('listening on: %s:%d' % (HOST, PORT))
    logging.info('wsdl is at: http://%s:%d/?wsdl' % (HOST, PORT))

    sys.exit(reactor.run())
