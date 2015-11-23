#!/usr/bin/env python

from os.path import join
from setuptools import setup, find_packages


name = 'geokey-epicollect'
version = __import__(name.replace('-', '_')).__version__
repository = join('https://github.com/ExCiteS', name)

setup(
    name=name,
    version=version,
    description='Use EpiCollect to collect data for GeoKey',
    url=repository,
    download_url=join(repository, 'tarball', version),
    author='Oliver Roick',
    author_email='excitesucl@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*']),
    include_package_data=True,
    install_requires=['lxml==3.3.5'],
)
