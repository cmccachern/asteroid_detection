==================
Get Data From WISE
==================


WISE images and associated datasets are available online through the Infrared Science Archive (IRSA). A description of their API's and how to use them can be found `HERE <https://irsa.ipac.caltech.edu/applications/Gator/GatorAid/irsa/catsearch.html>`_.

Datasets are also available through a URL. The way to access images this way is described in detail on the `IRSA website <https://irsa.ipac.caltech.edu/ibe/docs/wise/neowiser_yr6/yr6_i1bm_frm/>`_.

.. code-block:: python


    params = { 'scan_id': '01111r',
               'frame_num': 37,
               'band': 1,
             }
    params['scangrp'] = params['scan_id'][-2:]
    path = str.format(
        '{scangrp:s}/{scan_id:s}/{frame_num:03d}/{scan_id:s}{frame_num:03d}-w{band:1d}-int-1b.fits',
        **params)
    url = 'https://irsa.ipac.caltech.edu/ibe/data/wise/neowiser_yr6/yr6_i1bm_frm/' + path


For information on the Wise Survey, and what it is, IRSA briefly describes this in a `youtube video <https://www.youtube.com/watch?v=dmnIoIpN7I0&list=PL3UuvF_s8KWIZEwwFemmm7PeCDQFL5shU&index=14>`_.

