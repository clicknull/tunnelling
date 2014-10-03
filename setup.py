#!/usr/bin/env python
from setuptools import setup, find_packages
 
setup (
    name = "Tunnelling",
    version = "1.1",
    description="App and module for creating tunnels through SSH",
    author="Mario Rivas",
    author_email="h@cked.es", 
    url="http://github.com/gry/tunnelling",
    packages=['tunnelling'],
    # packages=find_packages(),
    entry_points = {
    'console_scripts': ['tunnelling = tunnelling.tunnelling:main']
                },
    download_url = "http://github.com/gry/tunnelling",
    zip_safe = True,
    install_requires = ['paramiko >= 1.7.7.1']
)



