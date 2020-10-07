"""
Python API client for Notify
"""
import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("notifications_utils/version.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

setup(
    name="notifications-utils",
    version=version,
    url="https://github.com/alphagov/notifications-utils",
    license="MIT",
    author="Government Digital Service",
    description="Shared python code for Notify",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "bleach~=3.1.4",
        "boto3~=1.10.38",
        "botocore~=1.13.35",
        "flask~=1.1.1",
        "flask-redis~=0.4.0",
        "itsdangerous~=1.1.0",
        "jinja2~=2.11.0",
        "mistune~=0.8.4",
        "monotonic~=1.5",
        "orderedset~=2.0.1",
        "phonenumbers~=8.11.0",
        "pypdf2~=1.26.0",
        "python-json-logger~=0.1.11",
        "pytz~=2019.3",
        "pyyaml~=5.3",
        "redis~=3.3.11",
        "requests~=2.22.0",
        "smartypants~=2.0.1",
        "statsd~=3.3.0",
        "werkzeug~=1.0.0",
    ],
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest~=6.1.1",
        "pytest-mock~=3.3.1",
        "requests-mock~=1.8.0",
        "freezegun~=1.0.0",
    ],
)
