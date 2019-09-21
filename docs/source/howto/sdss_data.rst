==================
Get Data From SDSS
==================

The `Sloan Digital Sky Survey <https://www.sdss.org>`_ has imaged one third of the sky, and its imagery is available for access through
it's Data Release, now currently on DR15.  There are many ways to view data drom SDSS.  Tools for accessing their
data are listed in the `data access page <https://www.sdss.org/dr15/data_access/>`_.  Data can be queried through SQL.
"Cooking with Sloan" has a `tutorial <http://www.skyserver.sdss.org/dr14/en/help/cooking/solarsystem/moving.aspx>`_
which gives an example SQL query to find moving objects, such as asteroids. See the
`schema browser <http://skyserver.sdss.org/dr15/en/help/browser/browser.aspx#&&history=description+PhotoObj+V>`_ for info on
all available data fields. SQL queries for DR15 can be submitted from their 
`SQL search form <http://skyserver.sdss.org/dr15/en/tools/search/sql.aspx>`_.  There is also a 
`how to find asteroids tutorial <http://skyserver.sdss.org/dr1/en/proj/basic/asteroids/findingasteroids2.asp>`_ that
has a link to the Get Fields tool and several example run, camcol, and field numbers which contain ateroids.
Once you know the run, camcol, and field, you can get data from a single field search.  Take a look at 
the search for `Run 752, Camcol 1, Field 373 <https://dr12.sdss.org/fields/runCamcolField?run=752&camcol=1&field=373>`_.
In the bottom left corner, you can see an asteroid in the image.  You can also download the jpg or fits files.

To access data programmatically, there is a python program called `Sciscript-Python <https://github.com/sciserver/SciScript-Python>`_
which can be used for insterfacing with CasJobs, a service that allows you to search for imagery from SDSS.

Another potentially useful resource will be the `SDSS moving object catalog <https://sbn.psi.edu/pds/resource/sdssmoc.html>`_,
which lists moving objects in the data from DR4.

