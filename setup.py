import os
import sys
from setuptools import setup
from textwrap import dedent

NAME = "kipavois"
REPO_SLUG = NAME + '-python'
GITHUB_ORG_URL = "https://github.com/cogniteev"
ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

version = '0.1'

setup(
    name=NAME,
    version=version,
    author="Tristan Carel",
    author_email="tristan@cogniteev.com",
    url= GITHUB_ORG_URL + '/' + REPO_SLUG,
    download_url="{0}/{1}/tarball/{2}".format(GITHUB_ORG_URL, REPO_SLUG, version),
    description="Flask proxy over Kibana with KiPavois",
    long_description=dedent("""
        Rationale
        ---------
        KiPavois is a NodeJS reverse proxy that allows you to filter
        Elasticsearch queries made by Kibana to filter-out documents
        the authenticated user is not allowed to see.

        This module provides a Flask Blueprint that allows you leverage the
        authentication model of your Flask application to authenticate users
        in Kibana.
    """),
    keywords="flask kipavois kibana authentication",
    packages=['kipavois'],
    install_requires=[
        'Flask >= 0.10.1',
        'requests >= 2.7.0'
    ],
    zip_safe=False,
    license="Apache license version 2.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ]
)
