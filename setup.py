#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **

# Setup file for the interaction-design tool

import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="robot-interaction-tool-ES",
    version="2.0.1",
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
        "qi"
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["idtool"],
    include_package_data=True,
    python_requires='>=2.7',
    entry_points={"console_scripts": ["idtool=interaction_manager.__main__:main"]}
)
