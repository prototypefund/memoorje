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
        "djangorestframework-camel-case~=1.2.0",
        "django-downloadview~=2.1.1",
        "django-filter~=2.4.0",
        "django-otp~=1.0.2",
        "git+https://github.com/robwa/django-rest-registration.git",
        "django-templated-email~=3.0.0",
        "djeveric~=1.0.0",
        "drf-spectacular~=0.18.2",
        "freezegun~=0.3.15",
        "html2text~=2020.1.16",
        "memoorje_crypto",
        "python-dateutil~=2.8.1",
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
