
import datetime
from lxml import etree

from spyne.decorator import rpc
from spyne.model.primitive import String
from spyne.service import ServiceBase

from spynepi.core import Project
from spynepi.core import release
from spynepi.core import Version
from spynepi.core import Developer
from spynepi.core import Person

class RdfService(ServiceBase):
    @rpc(String, _returns=Project)
    def get_doap(ctx, project_name):
        return Project(
            name="ornek",
            created=datetime.datetime.now(),
            shortdesc=u"Thanks for all the fish",
            homepage="",
            developer=Developer(Person=Person(name="Ugurcan",mbox="")),
            release=[
                release(
                    Version=Version(**{
                        "name": "ornek",
                         "created": datetime.datetime.now(),
                         "revision": 3.513,
                        'file-release': "hubele",
                    }),

                )
            ])


def _on_method_return_document(ctx):
    ctx.out_document = ctx.out_document[0]
    ctx.out_document.tag = "{http://usefulinc.com/ns/doap#}Project"
    ns0 = "{http://usefulinc.com/ns/doap#}"
    ns1 = "{http://xmlns.com/foaf/0.1/}"
    rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    xml = ctx.out_document
    xml.set(rdf+"about","/ornek")
    homepage = xml.find(ns0+"homepage")
    homepage.set(rdf+"resource","foo")
    mbox = xml.xpath("//ns0:developer//ns1:Person//ns1:mbox",
        namespaces={"ns0":"http://usefulinc.com/ns/doap#","ns1":"http://xmlns.com/foaf/0.1/"})
    mbox[0].set(rdf+"resource","foo")
    rlist = xml.findall(ns0+"release")
    for element in rlist:
        element.set(rdf+"about","spam")
        temp = element.find(ns0+"Version")
        fr = temp.find(ns0+"file-release")
        if fr is not None:
            fr.set(rdf+"resource","foo")
    print etree.tostring(xml,pretty_print=True)


RdfService.event_manager.add_listener('method_return_document', _on_method_return_document)