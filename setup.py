# This file is to support the development workflow.
#
# The setup.py is required to install a local directory in "editable"
# mode, that allows us to run tests against package modules.
"""Setup script for this package."""

import os

import setuptools

NAME = os.path.basename(os.path.dirname(__file__))

setuptools.setup(
    name=NAME,
    version='0.1',
    author='Andrei Polushin',
    author_email='polushin@gmail.com',
    description=NAME,
    long_description=NAME,
    long_description_content_type='text/markdown',
    url='https://github.com/anpol/' + NAME,
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
