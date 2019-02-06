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
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
    keywords='embedded development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'zeroconf',
        'paramiko'
    ],
    data_files=[('share/man/man1', ['man/mdt.1'])],
    package_data={
    },
    entry_points={
        'console_script': [
            'mdt=mdt:main',
        ],
    },
)
