import os
from setuptools import setup, find_packages

version = '0.1a'

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst')) as fp:
    longdesc = fp.read()

with open(os.path.join(here, 'CHANGELOG.rst')) as fp:
    longdesc += "\n\n" + fp.read()


setup(
    name='datacat',
    version=version,
    packages=find_packages(),
    url='http://github.com/rshk/datacat',
    license='Apache 2.0 License',
    author='Samuele Santi',
    author_email='s.santi@trentorise.eu',
    description='',
    long_description=longdesc,
    install_requires=[
        'Flask',
        # 'flask-restful',
        'psycopg2',
        'nicelog',
        'celery[redis]',
    ],
    # tests_require=tests_require,
    # test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        # 'License :: OSI Approved :: BSD License',
        # 'License :: OSI Approved :: MIT License',
        # 'License :: Public Domain',

        'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',

        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    package_data={'': ['README.rst', 'CHANGELOG.rst']},
    include_package_data=True,
    zip_safe=False)
