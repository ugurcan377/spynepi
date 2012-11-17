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

import datetime
import os

from sqlalchemy import sql

from spyne.decorator import rpc
from spyne.error import ArgumentError
from spyne.model.primitive import String
from spyne.model.primitive import Unicode
from spyne.service import ServiceBase

from spyne.model.binary import File
from spyne.protocol.http import HttpPattern

from spynepi.const import FILES_PATH
from spynepi.db import Package
from spynepi.db import Release
from spynepi.db import Distribution
from spynepi.db import Person


class RootService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, Unicode, File, Unicode, Unicode, Unicode,
         Unicode, Unicode, Unicode, Unicode, Unicode, Unicode, Unicode,
         Unicode, Unicode, String, _patterns=[HttpPattern("/",verb="POST")])
    def register(ctx, name, license, author, home_page, content, comment,
            download_url, platform, description, metadata_version, author_email,
            md5_digest, filetype, pyversion, summary, version, protcol_version):

        exists = False
        pth = os.path.join("files", name, version)

        def generate_package():
            return Package(
                    package_name=name,
                    package_cdate=datetime.date.today(),
                    package_description=description,
                    rdf_about=os.path.join("/", name),
                    package_license=license,
                    package_home_page=home_page
                )

        def generate_person():
            return Person(person_name=author,
                    person_email=author_email,
                )

        def generate_release():
            return Release(
                    rdf_about=os.path.join("/", name, version),
                    release_version=version,
                    release_cdate=datetime.date.today(),
                    release_summary=summary ,
                    meta_version=metadata_version,
                    release_platform=platform,
                )

        def generate_dist():
            return Distribution(content_name=content.name,
                    content_path=pth,
                    dist_download_url=download_url,
                    dist_comment=comment,
                    dist_file_type=filetype,
                    dist_md5=md5_digest,
                    py_version=pyversion,
                    protocol_version=protcol_version,
                )

        def package_content():
            file = content
            path = os.path.join(FILES_PATH,pth)
            if os.path.exists(path):
                f = open(os.path.join(path,file.name),"w")
            else:
                os.makedirs(path)
                f = open(os.path.join(path,file.name),"w")

            for d in file.data:
                f.write(d)
            f.close()

        body = ctx.in_body_doc

        #TO-DO Add a method check
        check = ctx.udc.session.query(Package).filter_by(package_name=name).all()
        if check != []:
            exists = True
            for rel in check[0].releases:
                if rel.release_version == version and os.path.exists(pth) == True:
                    raise ArgumentError()

        if body[":action"][0] == "submit":
            if exists:
                check[0].releases.append(generate_release())

            else:
                package = generate_package()
                package.owners.append(generate_person())
                package.releases.append(generate_release())
                ctx.udc.session.add(package)
                ctx.udc.session.flush()
            ctx.udc.session.commit()

        if body[":action"][0] == "file_upload":
            if exists:
                rel = ctx.udc.session.query(Release).join(Package).filter(
                    sql.and_(
                        Package.package_name == name,
                        Release.release_version == version)
                    ).first()

                rel.distributions.append(generate_dist())
                package_content()

            else:
                package = generate_package()
                package.owners.append(generate_person())
                package.releases.append(generate_release())
                package.releases[-1].distributions.append(generate_dist())
                package_content()
                ctx.udc.session.add(package)

            ctx.udc.session.commit()
