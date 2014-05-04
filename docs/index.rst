.. tagsana documentation master file, created by
   sphinx-quickstart on Sun May  4 18:16:26 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to tagsana's documentation!
===================================
Installing
----------
Install **tagsana** with
``pip install tagsana``.

Usage
-----
Get count of all tags in all workspaces::

    import tagsana
    t = tagsana.Tagsana()
    count = t.get_count()

The ``get_count`` method takes three parameters:
* ``wss`` - A string or list of strings of workspace IDs
* ``users`` - A string or list of strings of user IDs
* ``projs`` - A string or list of strings of project IDs

These parameters may be mixed and matched to delimit the desired Asana Tasks.

For example, to get a count of all tags in a single workspace::

    ws = '1557440990743'
    ws_count = t.get_count(wss=ws)

However, to get a count of all tags in a single workspace by a list of users::

    ws = '1557440990743'
    users = ['2347449870723','65745409982364']
    ws_count_by_users = t.get_count(ws, users)

Finally, to get a count of all tags in a list of projects::

    projs = ['4968349870754','90234099589364']
    ws_count_by_users = t.get_count(projs=projs)

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

