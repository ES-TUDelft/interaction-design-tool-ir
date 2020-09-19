#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **

# Setup file for the interaction-design tool

import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="robot-interaction-tool-ES",
    version="3.0.1",
    author="ES",
    author_email="e.saad@tudelft.nl",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="A design tool for prototyping human-robot interactions",
    license="MIT",
    url="https://github.com/ES-TUDelft/robot-interaction-tool",
    install_requires=[
        "pyyaml",
        "pymongo",
        "spotipy",
        "requests",
        "pyOpenSSL",
        "autobahn[twisted,serialization]",
        "PyQt5"
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["idtool"],
    include_package_data=True,
    python_requires='>=3.6',
    entry_points={"console_scripts": ["idtool=interaction_manager.__main__:main"]}
)
