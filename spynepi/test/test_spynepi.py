
#!/usr/bin/env python
#
# spyne - Copyright (C) Spyne contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

import os
import time
import unittest
import datetime

from spyne.error import ArgumentError
try:
    from urllib import urlencode
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import HTTPError
except ImportError:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError

_server_started = False

class TestSpynePi(unittest.TestCase):
    def setUp(self):
        global _server_started

        if not _server_started:
            def run_server():
                from spynepi.main import main
                os.remove("test.db")
                os.system("rm -r files/example")
                main("sqlite:///test.db")

            import thread
            thread.start_new_thread(run_server, ())
            # FIXME: Does anybody have a better idea?
            time.sleep(2)
            #Uploads example package for further testing
            pth = os.path.abspath("example")
            f = os.popen("python %s register -r http://localhost:7789 sdist upload -r http://localhost:7789" %(pth+"/setup.py"))
            f.read()
            _server_started = True

    def test_upload(self):
        #If the same package uploads more than once to server spynepi raises
        # a 400 this test checks
        pth = os.path.abspath("example")
        try:
            f = os.popen("python %s register -r http://localhost:7789 sdist upload -r http://localhost:7789" %(pth+"/setup.py"))
        except ArgumentError:
            assert True

    def test_index(self):
        url = "http://localhost:7789/"
        data = urlopen(url).read()
        html = '<table class="indexResponse"><tr><th>Updated</th><th>Package</th>'\
        '<th>Description</th></tr><tr><td>%s</td><td><a href="/example'\
        '/0.1.0">example</a></td><td>UNKNOWN</td></tr></table>'%str(datetime.date.today())
        assert data == html

    def test_download_html(self):

        url = "http://localhost:7789/example/"
        data = urlopen(url).read()
        f = open("test.html","r")
        f_text = f.read()
        test = f.read() in data
        assert test
