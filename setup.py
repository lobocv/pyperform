__author__ = 'lobocv'

from distutils.core import setup
from pyperform import __version__

setup(
    name='pyperform',
    packages=['pyperform'],  # this must be the same as the name above
    version=__version__,
    description='A fast and convenient way to performance test functions and compare results.',
    author='Calvin Lobo',
    author_email='calvinvlobo@gmail.com',
    url='https://github.com/lobocv/pyperform',
    download_url='https://github.com/lobocv/pyperform/tarball/%s' % __version__,
    keywords=['testing', 'performance', 'comparison', 'convenience', 'logging', 'timeit', 'speed', 'crash reporting'],
    classifiers=[],
)
