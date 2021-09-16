import os

from setuptools import find_namespace_packages, setup

from memoorje import __version__

__dir__ = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(__dir__, "README.md")) as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="memoorje",
    version=__version__,
    description="safe, self-determined digital inheritance for everyone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://memoorje.org",
    author="memoorje developers",
    author_email="tach@memoorje.org",
    license="AGPL-3.0-or-later",
    packages=find_namespace_packages(include=("memoorje", "memoorje.*")),
    install_requires=[
        "django~=3.2.7",
        "djangorestframework~=3.12.1",
        "djangorestframework-simplejwt~=4.8.0",
        "djoser~=2.1.0",
        "drf-spectacular~=0.18.2",
        "djangorestframework-camel-case~=1.2.0",
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django :: 3.2",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
