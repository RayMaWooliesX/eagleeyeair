import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="eagleeyeair",
    version="0.1.5",
    description="Python API client library for eagleeye",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/eagleeyeair/eagleeyeair",
    author="Cheng, Gang",
    author_email="cg1101@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=["eagleeyeair"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "realpython=eagleeyeair.__main__:main",
        ]
    },
)
