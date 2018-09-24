"""
Python API client for GOV.AU Notify
"""
import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('notifications_utils/version.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='notifications-utils',
    version=version,
    url='https://github.com/alphagov/notifications-utils',
    license='MIT',
    author='Government Digital Service',
    description='Shared python code for GOV.AU Notify.',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'bleach',
        'mistune',
        'request',
        'python-json-logger',
        'Flask',
        'orderedset',
        'Jinja2',
        'statsd',
        'Flask-Redis',
        'pyyaml',
        'phonenumbers',
        'pytz',
        'smartypants',
        'monotonic',
        'pypdf2',
        'boto3~=1.8'
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest',
        'pytest-mock',
        'pytest-cov',
        'requests-mock',
        'freezegun',
        'flake8',
    ],
)
