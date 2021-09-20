import os

from setuptools import find_namespace_packages, setup

from memoorje_crypto import __version__

__dir__ = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(__dir__, "README.md")) as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="memoorje_crypto",
    version=__version__,
    description="Web-compatible encryption formats for memoorje.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://memoorje.org",
    author="memoorje developers",
    author_email="tach@memoorje.org",
    license="MIT",
    packages=find_namespace_packages(include=("memoorje_crypto", "memoorje_crypto.*")),
    install_requires=[
        "pycryptodome~=3.6",
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Security :: Cryptography",
    ],
)
