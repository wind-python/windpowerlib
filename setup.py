import os
from setuptools import setup
from windpowerlib import __version__

setup(name='windpowerlib',
      version=__version__,
      description='Creating time series from wind power plants.',
      url='http://github.com/wind-python/windpowerlib',
      author='oemof developing group',
      author_email='mail',
      license=None,
      packages=['windpowerlib'],
      package_data={
          'windpowerlib': [os.path.join('data', '*.csv')]},
      zip_safe=False,
      install_requires=['numpy >= 1.7.0',
                        'pandas >= 0.13.1'])
