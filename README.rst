.. image:: https://img.shields.io/pypi/v/geokey-epicollect.svg
    :alt: PyPI Package
    :target: https://pypi.python.org/pypi/geokey-epicollect

.. image:: https://img.shields.io/travis/ExCiteS/geokey-epicollect/master.svg
    :alt: Travis CI Build Status
    :target: https://travis-ci.org/ExCiteS/geokey-epicollect

.. image:: https://img.shields.io/coveralls/ExCiteS/geokey-epicollect/master.svg
    :alt: Coveralls Test Coverage
    :target: https://coveralls.io/r/ExCiteS/geokey-epicollect

geokey-epicollect
=================

Use `EpiCollect <http://www.epicollect.net>`_'s phone app as a mobile client to collect data and store it with `GeoKey <http://geokey.org.uk>`_.

Install
-------

geokey-epicollect requires:

- Python version 2.7
- GeoKey version 0.9 or greater

Make sure these dependencies are installed:

.. code-block:: console
    sudo apt-get install libxml2-dev
    sudo apt-get install libxslt1-dev

Install the extension from PyPI:

.. code-block:: console

    pip install geokey-epicollect

Or from cloned repository:

.. code-block:: console

    cd geokey-epicollect
    pip install -e .

Add the package to installed apps:

.. code-block:: console

    INSTALLED_APPS += (
        ...
        'geokey_epicollect',
    )

Migrate the models into the database:

.. code-block:: console

    python manage.py migrate geokey_epicollect

You're now ready to go!

Test
----

Run tests:

.. code-block:: console

    python manage.py test geokey_epicollect

Check code coverage:

.. code-block:: console

    coverage run --source=geokey_epicollect manage.py test geokey_epicollect
    coverage report -m --omit=*/tests/*,*/migrations/*
