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
import subprocess

from urllib2 import HTTPError
from urllib2 import urlopen

from lxml import html

from pkg_resources import resource_filename

from setuptools.command.easy_install import main as easy_install

from spyne.decorator import rpc
from spyne.error import RequestNotAllowed
from spyne.error import ResourceNotFoundError
from spyne.model.binary import File
from spyne.model.complex import Array
from spyne.model.primitive import AnyUri
from spyne.model.primitive import Unicode
from spyne.protocol.html import HtmlPage
from spyne.protocol.http import HttpPattern
from spyne.service import ServiceBase

from spynepi.const import FILES_PATH
from spynepi.const import REPO_NAME
from spynepi.core import Index
from spynepi.core import Release
from spynepi.entity.root import Package
from spynepi.entity.root import Release
from sqlalchemy.orm.exc import NoResultFound


TPL_DOWNLOAD = os.path.abspath(resource_filename("spynepi.const.template",
                                                               "download.html"))


class IndexService(ServiceBase):
    @rpc (_returns=Array(Index), _patterns=[HttpPattern("/",verb="GET")])
    def index(ctx):
        idx = []
        packages = ctx.udc.session.query(Package).all()
        for package in packages:
            idx.append(Index(
                Updated=package.package_cdate,
                Package=AnyUri.Value(text=package.package_name,
                    href=package.releases[-1].rdf_about),
                Description=package.package_description,
            ))

        return idx


def cache_packages(project_name):
    path = os.path.join(FILES_PATH,"files","tmp")
    if not os.path.exists(path):
        os.makedirs(path)
    easy_install(["--user","-U","--build-directory",path,project_name])
    dpath = os.path.join(path,project_name)
    dpath = os.path.abspath(dpath)
    if not dpath.startswith(path):
        # This request tried to read arbitrary data from the filesystem
        raise RequestNotAllowed(repr([project_name,]))
    command = ["python", "setup.py", "register", "-r", REPO_NAME, "sdist",
                                                "upload", "-r", REPO_NAME]
    subprocess.call(command, cwd=dpath)


class HtmlService(ServiceBase):
    @rpc(Unicode, Unicode,_returns=Unicode, _patterns=[
            HttpPattern("/<project_name>"),
            HttpPattern("/<project_name>/"),
            HttpPattern("/<project_name>/<version>"),
            HttpPattern("/<project_name>/<version>/"),
        ])
    def download_html(ctx,project_name,version):
        ctx.transport.mime_type = "text/html"

        try:
            ctx.udc.session.query(Package).filter_by(
                                            package_name=project_name).one()
        except NoResultFound:
            try:
                data = urlopen("http://pypi.python.org/simple/%s"%(project_name)).read()
                cache_packages(project_name)
            except HTTPError:
                raise ResourceNotFoundError()

        if version:
            query = ctx.udc.session.query(Package,Release).\
                    filter(Package.package_name==project_name).\
                    filter(Release.release_version==version).\
                    filter(Package.id==Release.package_id).all()
            pack, ver = query[0]
            download = HtmlPage(TPL_DOWNLOAD)
            download.title = project_name
            download.link.attrib["href"] = os.path.join(ver.rdf_about,"doap.rdf")
            download.h1 = project_name+"-"+version
            download.a = ver.distributions[0].content_name
            download.a.attrib["href"] = os.path.join("/",ver.distributions[0].content_path,
                ver.distributions[0].content_name
                + "#md5=" + ver.distributions[0].dist_md5)

        else:
            package = ctx.udc.session.query(Package) \
                                     .filter_by(package_name=project_name).one()

            download = HtmlPage(TPL_DOWNLOAD)
            download.title = project_name
            download.link.attrib["href"] = os.path.join(package.releases[-1].rdf_about,"doap.rdf")
            download.h1 = project_name
            download.a = package.releases[-1].distributions[0].content_name
            download.a.attrib["href"] = os.path.join("/",
                package.releases[-1].distributions[0].content_path,
                    "%s#md5=%s" % (
                        package.releases[-1].distributions[0].content_name,
                        package.releases[-1].distributions[0].dist_md5
                    )
                )

        return html.tostring(download.html)

    @rpc(Unicode, Unicode, Unicode, _returns=File, _patterns=[
            HttpPattern("/files/<project_name>/<version>/<file_name>")])
    def download_file(ctx, project_name, version, file_name):
        repository_path = os.path.abspath(os.path.join(FILES_PATH,"files"))
        file_path = os.path.join(repository_path, project_name, version, file_name)
        file_path = os.path.abspath(file_path)

        if not file_path.startswith(repository_path):
            # This request tried to read data from where it's not supposed to
            raise RequestNotAllowed(repr([project_name, version, file_name]))

        return File.Value(name=file_name, path=file_path)
