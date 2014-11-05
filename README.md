# geokey-epicollect


Use [EpiCollect](http://www.epicollect.net/)'s phone app as a mobile client to collect data and store it with [GeoKey](http://geokey.org.uk). 

## Quick start

1. Add "geokey-epicollect" to your INSTALLED_APPS setting like this:

    ```
        INSTALLED_APPS = (
            ...
            'geokey-epicollect',
        )
    ```

2. Include the polls URLconf in your project urls.py like this:

    ```
        url(r'^epicollect/', include('geokey-epicollect.urls', namespace='epicollect')),
    ```
