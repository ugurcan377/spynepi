
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

import os

from spyne.decorator import rpc
from spyne.model.primitive import Unicode
from spyne.service import ServiceBase

from spynepi.core import Developer
from spynepi.core import Person
from spynepi.core import Project
from spynepi.core import Release
from spynepi.core import Version
from spynepi.entity.root import Package
from spynepi.entity.root import Person
from spynepi.entity.root import Release

from werkzeug.routing import Rule

class RdfService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=Project, _http_routes=[
            Rule("/<string:project_name>/<string:version>/doap.rdf"),
            Rule("/<string:project_name>/doap.rdf")
        ])
    def get_doap(ctx, project_name, version):
        package = ctx.udc.session.query(Package).filter_by(package_name=project_name).one()
        release_=[]
        for rel in package.releases:
            release_.append( Release(about=rel.rdf_about,
                    Version=Version(**{
                        "name": package.package_name,
                         "created": rel.release_cdate,
                         "revision": rel.release_version,
                        'file-release': (rel.distributions[0].content_name),
                        "resource": rel.distributions[0].content_path+"/"+
                            rel.distributions[0].content_name+"#"
                            +rel.distributions[0].dist_md5
                    })

                ))

        return Project(
            about=os.path.join("/",package.package_name),
            name=package.package_name,
            created=package.package_cdate,
            shortdesc=package.package_description,
            homepage=package.package_home_page,
            developer=Developer(Person=Person(name=package.owners[0].person_name,
                mbox=package.owners[0].person_email)),
            release=release_)


def _on_method_return_document(ctx):
    ctx.out_document = ctx.out_document[0]
    ctx.out_document.tag = "{http://usefulinc.com/ns/doap#}Project"


RdfService.event_manager.add_listener('method_return_document', _on_method_return_document)
