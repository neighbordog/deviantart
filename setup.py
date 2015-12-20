from setuptools import setup

setup(
    name="deviantart",
    version="0.1.2",
    description="A Python wrapper for the DeviantArt API",
    author="Kevin Eichhorn",
    author_email="kevineichhorn@me.com",
    packages=["deviantart"],
    install_requires=[
        "sanction"
    ]
)