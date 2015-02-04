# geokey-epicollect


Use [EpiCollect](http://www.epicollect.net/)'s phone app as a mobile client to collect data and store it with [GeoKey](http://geokey.org.uk).

## Install

Make sure these dependencies are installed

```
sudo apt-get install libxml2-dev
sudo apt-get install libxslt1-dev
```

## Quick start

1. Add "geokey_epicollect" to your INSTALLED_APPS settings (`core/settings/project.py`) like this:

    ```
        INSTALLED_APPS = (
            ...
            'geokey_epicollect',
        )
    ```

2. Include the epicollect URLconf in your extensions urls.py (`core/url/extensios.py`) like this:

    ```
        url(r'^epicollect/', include('geokey_epicollect.urls', namespace='epicollect')),
    ```
