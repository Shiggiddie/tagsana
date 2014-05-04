from setuptools import setup, find_packages
from tagsana import __version__ as version

install_requires = []
try:
        import requests
except ImportError:
        install_requires.append("requests")

name = "tagsana"

setup(
    name = name, version = version, author = "Sean Dennison",
    author_email = "sean.dennison.osu@gmail.com",
    description = "Visualizer for Asana task tags",
    license = "Apache License, (2.0)",
    keywords = "tagsana",
    url = "https://github.com/Shiggiddie/tagsana",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=install_requires,
    )
