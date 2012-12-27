Spynepi
=======

This is a caching PyPI implementation that can be used as a standalone PyPI server
as well as a PyPI cache.

As the name suggests, it is using `spyne http://pypi.python.org/pypi/spyne`

Requirements
------------
Spynepi uses some subsystems of spyne which requires optional dependencies. And also spynepi uses twisted as wsgi server

* Spyne http://github.com/arskom/spyne
* Twisted http://twistedmatrix.com/
* SQLAlchemy http://sqlalchemy.org
* Werkzeug http://werkzeug.pocoo.org/

Installation
------------

You can get spynepi via pypi: ::

    easy_install spynepi

or you can clone from github: ::

    git clone git://github.com/arskom/spynepi.git

or get the source distribution from one of the download sites and unpack it.

To install from source distribution, you should run its setup script as usual: ::

    python setup.py install

And if you want to make any changes to the spynepi code, it's more comfortable to
use: ::

    python setup.py develop

Using Spynepi
-------------

You can start spynepi with: :: 

    $ spynepi_daemon

You can upload packages with: ::  

    $ python setup.py register -r local sdist upload -r spynepi

And you can download packages with: ::  
    
    $ easy_install --user -U -i http://localhost:7789 package


Configuration
-------------

Config file for spynepi can be found inside ``spynepi/const/__init__.py`` 

* DB_CONNECTION_STRING : Default database for spynepi is sqlite. If you wish to use a different database you can change this line. It must be an sqlalchemy compatiable database connection string
  
  For detatils please read http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html  

  Example: for postgres ``postgresql://user:password@localhost:5432/database_name``

* FILES_PATH : Path which packages will be stored in default it creates a file named files

* HOST : Thank you Captain Obvious.  
  Default is 0.0.0.0

* PORT : Thanks again you're awesome.  
  Default is 7789

* REPO_NAME: The repository name you will use to upload or download packages in default it is spynepi. 

* TABLE_PREFIX: Prefix for tables which sqlalchemy will create

