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

from werkzeug.routing import Rule

from spyne.decorator import rpc
from spyne.model.primitive import Unicode
from spyne.model.primitive import Integer
from spyne.model.primitive import AnyUri
from spyne.model.primitive import UriValue
from spyne.model.primitive import Float
from spyne.model.complex import Array
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
