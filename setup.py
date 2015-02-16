import os
del os.link

from distutils.core import setup

setup(
    # Application name:
    name="geokey-epicollect",

    description='Enables GeoKey to be used with EpiCollect for data collection.',

    # Version number (initial):
    version="0.1.0-beta-2",

    # Application author details:
    author="Oliver Roick",
    author_email="o.roick@ucl.ac.uk",

    url = 'https://github.com/ExCiteS/geokey-epicollect', # use the URL to the github repo
    download_url = 'https://github.com/ExCiteS/geokey-epicollect/tarball/0.1-beta-2',

    # Packages
    packages=["geokey_epicollect"],

    # Include additional files into the package
    include_package_data=True,

    # Dependent packages (distributions)
    install_requires=[
        'lxml==3.3.5'
    ],
)
