# cm-epicollect


Use [EpiCollect](http://www.epicollect.net/)'s phone app as a mobile client to collect data and store it with Community Maps. 

## Quick start

1. Add "cm\_epicollect" to your INSTALLED_APPS setting like this:

    ```
        INSTALLED_APPS = (
            ...
            'cm_epicollect',
        )
    ```

2. Include the polls URLconf in your project urls.py like this:

    ```
        url(r'^epicollect/', include('cm_epicollect.urls', namespace='epicollect')),
    ```
