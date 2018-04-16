"""
Python API client for GOV.UK Notify
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
    description='Shared python code for GOV.UK Notify.',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'bleach==2.1.3',
        'mistune==0.8.3',
        'requests==2.18.4',
        'python-json-logger==0.1.8',
        'Flask>=0.12.2',
        'orderedset==2.0.1',
        'Jinja2==2.10',
        'statsd==3.2.2',
        'Flask-Redis==0.3.0',
        'pyyaml==3.12',
        'phonenumbers==8.9.3',
        'pytz==2018.4',
        'smartypants==2.0.1',
        'monotonic==1.4',
        'pypdf2==1.26.0',
        'awscli==1.14.62',
        'boto3==1.6.8'
    ],
)
