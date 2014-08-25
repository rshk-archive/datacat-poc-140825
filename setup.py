import os
from setuptools import setup, find_packages

version = 'INSERT_VERSION_HERE'

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst')) as fp:
    longdesc = fp.read()

with open(os.path.join(here, 'CHANGELOG.rst')) as fp:
    longdesc += fp.read()


setup(
    name='PACKAGE_NAME',
    version=version,
    packages=find_packages(),
    url='PACKAGE_URL',
    license='BSD License',  # Apache 2.0 License
    author='',
    author_email='',
    description='',
    long_description=longdesc,
    install_requires=[],
    # tests_require=tests_require,
    # test_suite='tests',
    classifiers=[
        # 'License :: OSI Approved :: Apache Software License',
        # 'License :: OSI Approved :: BSD License',
        # 'License :: OSI Approved :: MIT License',
        # 'License :: Public Domain',

        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',

        # 'Programming Language :: Python :: 2.6',
        # 'Programming Language :: Python :: 2.7',
    ],
    package_data={'': ['README.rst', 'CHANGELOG.rst']},
    include_package_data=True,
    zip_safe=False)
