from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mdt',
    version='1.0',
    description='A command-line tool to manage Mendel embedded systems',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://aiyprojects.googlesource.com/mdt.git',
    author='Mendel Linux Software Team',
    author_email='support-aiyprojects@google.com',
    classifiers = [
        # 3 -> Alpha
        # 4 -> Beta
        # 5 -> Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development',

        'License :: OSI Approved :: Apache License',

        'Programming Language :: Python :: 3',
    ],
    keywords='embedded development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'zeroconf',
        'paramiko'
    ],
    package_data={
        'default_mendel_ssh_key', [ 'data/mendel_ssh_id', 'data/mendel_ssh_id.pub' ],
    },
    entry_points={
        'console_script': [
            'mdt=mdt:main',
        ],
    },
)
