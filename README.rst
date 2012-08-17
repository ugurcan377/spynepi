Spynepi
=======

This is a caching PyPI implementation that can be used as a standalone PyPI server
as well as a PyPI cache.

As the name suggests, it is using `spyne <http://pypi.python.org/pypi/spyne>`

Requirements
------------
Spynepi uses some subsystems of spyne which requires optional dependencies. And also spynepi uses twisted as wsgi server

* Spyne <http://github.com/arskom/spyne>
* Twisted <http://twistedmatrix.com/>
* SQLAlchemy <http://sqlalchemy.org>
* Werkzeug <http://werkzeug.pocoo.org/>

Installation
------------

You can get spynepi via pypi: ::

    easy_install spynepi

or you can clone from github: ::

    git clone git://github.com/ugurcan377/spynepi.git

or get the source distribution from one of the download sites and unpack it.

To install from source distribution, you should run its setup script as usual: ::

    python setup.py install

And if you want to make any changes to the spynepi code, it's more comfortable to
use: ::

    python setup.py develop

Setup
-----

Assuming you are running your site locally for now, add the following to 
your ``~/.pypirc`` file::

    [distutils]
    index-servers =
        pypi
        local

    [pypi]
    username:user
    password:secret

    [local]
    username:user
    password:secret
    repository:http://localhost:7789

Then you must set some settings for spynepi which is inside ``spynepi/const/__init__.py`` 

* DB_ CONNECTION_ STRING : Must be an sqlalchemy compatiable database connection string
For detatils please read <http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html>  
Example: for postgres `postgresql://user:password@localhost:5432/database_name`

* FILES_PATH : An (absolute) path which packages will be stored  
Example: ``/home/foo/workspace/spynepi``

* HOST : Thank you Captain Obvious.  
  Default is 0.0.0.0

* PORT : Thanks again you're awesome.  
  Default is 7789

* REPO_NAME: The repository name you wrote in pypirc

* TABLE_PREFIX: Prefix for tables which sqlalchemy will create

Using Spynepi
-------------

You can start spynepi with: :: 

    $ spynepi_daemon

You can upload packages with: ::  

    $ python setup.py register -r local sdist upload -r local

And you can download packages with: ::  
    
    $ easy_install --user -U -i http://localhost:7789 package


