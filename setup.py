import os.path
import re

from setuptools import find_packages, setup


def read(*parts):
    with open(os.path.join(*parts)) as f:
        return f.read().strip()


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*\"([\d.abrc]+)\"")
    init_py = os.path.join(os.path.dirname(__file__), "sse", "__init__.py")
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        raise RuntimeError(f"Cannot find version in {init_py}")


classifiers = [
    "License :: OSI Approved :: MIT License",
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3 :: Only",
    "Operating System :: POSIX",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Framework :: AsyncIO",
]

install_requires = [
    "sanic",
    "redis",
    "aiopubsub-py3"
]

setup(
    name="sanic-sse-py3",
    version=read_version(),
    description="aio sanic sse ",
    long_description="\n\n".join((read("README.rst"), read("CHANGELOG.md"))),
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    keywords="aio redis pubsub sanic sse",
    platforms=["POSIX"],
    url="https://github.com/daleeg/sanic_sse",
    license="MIT",
    packages=find_packages(exclude=["docs"]),
    install_requires=install_requires,
    python_requires=">=3.8",
    include_package_data=True,
)
