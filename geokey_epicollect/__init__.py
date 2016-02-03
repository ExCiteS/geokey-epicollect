from geokey.extensions.base import register


VERSION = (0, 2, 2)
__version__ = '.'.join(map(str, VERSION))

register(
    'geokey_epicollect',
    'EpiCollect',
    display_admin=True,
    superuser=False,
    version=__version__
)
