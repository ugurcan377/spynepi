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

from spyne.model.complex import ComplexModel
from spyne.model.complex import XmlAttribute

from spyne.model.primitive import AnyUri
from spyne.model.primitive import Date
from spyne.model.primitive import String
from spyne.model.primitive import Unicode

from spyne.util.odict import odict

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

#print "!"*45,Version._type_info["file-release"].Attributes.resource


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
