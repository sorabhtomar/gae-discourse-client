import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="gae-discourse-client",
    version="0.0.1",
    author="Thomas Davids",
    author_email="thomas@udacity.com",
    description=("An API client for Discourse using the Google App Engine "
                 "framework"),
    license="MIT",
    keywords="google appengine discourse api client",
    url="https://github.com/udacity/gae-discourse-client",
    packages=['src', 'tests'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
