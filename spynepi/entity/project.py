
import datetime

from spyne.decorator import rpc
from spyne.model.primitive import String
from spyne.service import ServiceBase

from spynepi.core import Project
from spynepi.core import Release
from spynepi.core import Version
from spynepi.core import Developer
from spynepi.core import FileRelease
from spynepi.core import Person

class RdfService(ServiceBase):
    @rpc(String, _returns=Project)
    def get_doap(ctx, project_name):
        return Project(
            name="ornek",
            created=datetime.datetime.now(),
            developer=Developer(Person=Person(name="Ugurcan")),
            release=[
                Release(
                    Version=Version(**{
                        "name": "ornek",
                        "resource": "hebele",
                        'file-release': FileRelease(**{
                            "resource": "hubele",
                            "file-release": "hede"
                        }),
                    }),
                    about="hubele",
                )
            ])
