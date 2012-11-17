
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

from spyne.decorator import rpc
from spyne.model.complex import ComplexModel
from spyne.model.complex import XmlAttribute
from spyne.model.primitive import AnyUri
from spyne.model.primitive import Date
from spyne.model.primitive import String
from spyne.model.primitive import Unicode
from spyne.service import ServiceBase
from spyne.protocol.http import HttpPattern

from spyne.util.odict import odict

from spynepi.db import Package
from spynepi.db import Person
from spynepi.db import Release


class RdfResource(XmlAttribute):
    __type_name__ = "resource"
    __namespace__ = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


class Version(ComplexModel):
    __namespace__ = "http://usefulinc.com/ns/doap#"

    _type_info = odict([
        ('name', String),
        ('created', Date),
        ('revision', String),
        #ns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        #TO-DO Add path#md5 -> rdf:resource as atrribute
        ('file-release', String),
        ("resource", RdfResource(String, ns="http://www.w3.org/1999/02/22-rdf-syntax-ns#", attribute_of="file-release")),
    ])


class RdfAbout(XmlAttribute):
    __type_name__ = "about"
    __namespace__ = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


class Release(ComplexModel):
    __namespace__ = "http://usefulinc.com/ns/doap#"

    _type_info = odict([
        ('about', RdfAbout(String, ns="http://www.w3.org/1999/02/22-rdf-syntax-ns#")),
        ('Version', Version),
    ])


class Person(ComplexModel):
    __namespace__ = "http://xmlns.com/foaf/0.1/"

    _type_info = odict([
        ('name', String),
        #TO-DO Add atrribute
        ('mbox', String),
    ])


class Developer(ComplexModel):
    __namespace__ = "http://xmlns.com/foaf/0.1/"
    _type_info = odict([
        ('Person', Person)
    ])


class Project(ComplexModel):
    __namespace__ = "http://usefulinc.com/ns/doap#"

    _type_info = odict([
        ('about', RdfAbout(String, ns="http://www.w3.org/1999/02/22-rdf-syntax-ns#")),
        ('name', String),
        ('created', Date),
        ('shortdesc', Unicode),
        ('homepage', String),
        ('developer', Developer),
        ('release', Release.customize(max_occurs=float('inf'))),
    ])


class Index(ComplexModel):
    _type_info = odict([
        ("Updated", Date),
        ("Package", AnyUri),
        ("Description", String),
    ])


class RdfService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=Project, _patterns=[
            HttpPattern("/<project_name>/doap.rdf"),
            HttpPattern("/<project_name>/<version>/doap.rdf"),
        ])
    def get_doap(ctx, project_name, version):
        package = ctx.udc.session.query(Package).filter_by(package_name=project_name).one()

        return Project(
            about=package.package_name,
            name=package.package_name,
            created=package.package_cdate,
            shortdesc=package.package_description,
            homepage=package.package_home_page,
            developer=Developer(
                Person=Person(
                    name=package.owners[0].person_name,
                    mbox=package.owners[0].person_email
                )
            ),
            release=(
                Release(
                    about=rel.rdf_about,
                    Version=Version(**{
                        "name": package.package_name,
                        "created": rel.release_cdate,
                        "revision": rel.release_version,
                        'file-release': rel.distributions[0].content_name,
                        "resource": '%s/%s#%s' % (
                            rel.distributions[0].content_path,
                            rel.distributions[0].content_name,
                            rel.distributions[0].dist_md5,
                        )
                    })
                )
                for rel in package.releases
            )
        )


def _on_method_return_document(ctx):
    ctx.out_document = ctx.out_document[0]
    ctx.out_document.tag = "{http://usefulinc.com/ns/doap#}Project"


RdfService.event_manager.add_listener('method_return_document',
                                                     _on_method_return_document)
