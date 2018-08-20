
from setuptools import setup, find_packages

setup(
    name='todoapp',
    version='0.1',
    description='Todo app and plan manager',
    url='https://bitbucket.org/zxdcm/isppythonlabs/',
    author='Egor Kirilin',
    author_email='z@xd.cm',
    packages=find_packages(exclude=['tests']),
    install_requires=['sqlalchemy', 'python-dateutil'],
    entry_points={
        'console_scripts': ['todoapp=client.main:main']
    },
    test_suite='tests'
)
