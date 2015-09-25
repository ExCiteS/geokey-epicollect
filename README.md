# geokey-epicollect


Use [EpiCollect](http://www.epicollect.net/)'s phone app as a mobile client to collect data and store it with [GeoKey](http://geokey.org.uk).

## Install

Make sure these dependencies are installed

```
sudo apt-get install libxml2-dev
sudo apt-get install libxslt1-dev
```

Install the package

```
sudo pip install geokey-epicollect
```

## Quick start

1. Add "geokey_epicollect" to your INSTALLED_APPS settings (`settings/local_settings.py`) like this:

    ```
        INSTALLED_APPS = (
            ...
            'geokey_epicollect',
        )
    ```

2. Add the epicollect table to the db like this:

    ```
        ../env/bin/python manage.py migrate
    ```
