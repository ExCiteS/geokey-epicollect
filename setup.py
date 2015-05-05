from setuptools import setup

setup(
    # Application name:
    name="geokey_epicollect",

    description='Enables GeoKey to be used with EpiCollect for data collection.',

    # Version number (initial):
    version="0.2.0",

    # Application author details:
    author="Oliver Roick",
    author_email="o.roick@ucl.ac.uk",

    url='https://github.com/ExCiteS/geokey-epicollect',
    download_url='https://github.com/excites/geokey-epicollect/releases',

    # Packages
    packages=["geokey_epicollect"],

    package_data={'geokey_epicollect': ['templates/*.html', 'migrations/*.py']},

    # Include additional files into the package
    include_package_data=True,

    # Dependent packages (distributions)
    install_requires=[
        'lxml==3.3.5'
    ],
)
