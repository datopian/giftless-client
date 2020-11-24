from setuptools import find_packages, setup

import giftless_client

with open('README.md') as f:
    long_description = f.read()

setup(
    name='giftless-client',
    packages=find_packages(exclude='./tests'),
    version=giftless_client.__version__,
    description='A Git LFS client implementation in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/datopian/giftless-client',
    author='Shahar Evron',
    author_email='shahar.evron@datopian.com',
    install_requires=[
        'click',
        'requests',
        'python-dateutil',
        'typing-extensions'
    ],
    package_data={},
    entry_points={
        'console_scripts': [
            'giftless-client = giftless_client.main:main',
        ]
    },
)
