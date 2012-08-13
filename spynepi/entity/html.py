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

from lxml import html

from werkzeug.routing import Rule

from spyne.decorator import rpc
from spyne.model.primitive import Unicode
from spyne.model.primitive import Integer
from spyne.model.primitive import AnyUri
from spyne.model.primitive import UriValue
from spyne.model.primitive import Float
from spyne.model.complex import Array
from spyne.model.binary import File
from spyne.protocol.html import HtmlPage
from spyne.service import ServiceBase

from spynepi.core import Project
from spynepi.core import Release
from spynepi.core import Version
from spynepi.core import Developer
from spynepi.core import Person
from spynepi.core import Index
from spynepi.entity.root import Package
from spynepi.entity.root import Release
from spynepi.entity.root import Person
from spynepi.entity.root import Distribution

class IndexService(ServiceBase):
    @rpc (_returns=Array(Index), _http_routes=[Rule("/",methods=["GET"])])
    def index(ctx):
        idx = []
        packages = ctx.udc.session.query(Package).all()
        for package in packages:
            idx.append(Index(
                Updated=package.package_cdate,
                Package=UriValue(text=package.package_name,
                    href=package.releases[-1].rdf_about),
                Description=package.package_description,
            ))

        return idx


class HtmlService(ServiceBase):
    @rpc(Unicode, Unicode,_returns=Unicode, _http_routes=[
            Rule("/<string:project_name>/<string:version>/"),
            Rule("/<string:project_name>/<string:version>"),
            Rule("/<string:project_name>/"),
            Rule("/<string:project_name>")
        ])
    def download_html(ctx,project_name,version):
        ctx.transport.mime_type = "text/html"
        if version:
            hede = ctx.udc.session.query(Package,Release).\
            filter(Package.package_name==project_name).\
            filter(Release.release_version==version).\
            filter(Package.id==Release.package_id).all()
            pack,ver = hede[0]
            download = HtmlPage("template/download.html")
            download.title = project_name
            download.link.attrib["href"] = os.path.join(ver.rdf_about,"doap.rdf")
            download.h1 = project_name+"-"+version
            download.a = ver.distributions[0].content_name
            download.a.attrib["href"] = os.path.join("/",ver.distributions[0].content_path,
                ver.distributions[0].content_name
                + "#md5=" + ver.distributions[0].dist_md5)
        else:
            package = ctx.udc.session.query(Package).filter_by(
                                            package_name=project_name).one()

            download = HtmlPage("template/download.html")
            download.title = project_name
            download.link.attrib["href"] = os.path.join(package.releases[-1].rdf_about,"doap.rdf")
            download.h1 = project_name
            download.a = package.releases[-1].distributions[0].content_name
            download.a.attrib["href"] = os.path.join("/",package.releases[-1].distributions[0].content_path,
                package.releases[-1].distributions[0].content_name
                + "#md5=" + package.releases[-1].distributions[0].dist_md5)
        


        return html.tostring(download.html)

    @rpc(Unicode, Unicode, Unicode, _returns=File, _http_routes=[
            Rule("/files/<string:project_name>/<string:version>/<string:download>")])
    def download_file(ctx,project_name,version,download):
        pth = os.path.join(os.getcwd(),"files",project_name,version,download)

        return File(name=download, type="application/x-tar", path=pth)
