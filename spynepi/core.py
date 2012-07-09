
from spyne.model.complex import ComplexModel
from spyne.model.complex import XmlAttribute
from spyne.model.primitive import AnyUri
from spyne.model.primitive import Date
from spyne.model.primitive import Float
from spyne.model.primitive import String
from spyne.model.primitive import Unicode

from spyne.util.odict import odict

class FileRelease(ComplexModel):
    __namespace__ = "http://usefulinc.com/ns/doap#"
# TO-DO Wait for the primitive XmlAttribute support
    _type_info = odict([
        ('resource', XmlAttribute(String)),
#        ('file-release', String)
    ])


class Version(ComplexModel):
    __namespace__ = "http://usefulinc.com/ns/doap#"

    _type_info = odict([
        ('name', String),
        ('created', Date),
        ('revision', Float),
 #ns="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        #TO-DO Add path#md5 -> rdf:resource as atrribute
        ('file-release', FileRelease),
    ])


class Release(ComplexModel):
    __namespace__ = "http://usefulinc.com/ns/doap#"

    _type_info = odict([
        ('about', XmlAttribute(String)),
        ('Version', Version)
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
        ('Person',Person)
    ])



class Project(ComplexModel):
    __namespace__ = "http://usefulinc.com/ns/doap#"

    _type_info = odict([
        ('name', String),
        ('created', Date),
        ('shortdesc', Unicode),
        ('homepage', AnyUri),
        ('developer', Developer),
        ('release', Release.customize(max_occurs=float('inf'))),
    ])

import datetime

print Project(name="ornek", created=datetime.datetime.now(), release=[Release(Version=Version(name="ornek"))])
