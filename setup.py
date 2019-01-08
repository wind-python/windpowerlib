import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='windpowerlib',
      version='0.0.6',
      description='Creating time series from wind power plants.',
      url='http://github.com/wind-python/windpowerlib',
      author='oemof developing group',
      author_email='mail',
      license=None,
      packages=['windpowerlib'],
      package_data={
          'windpowerlib': [os.path.join('data', '*.csv')]},
      long_description=read('README.rst'),
      zip_safe=False,
      install_requires=['numpy >= 1.7.0',
                        'pandas >= 0.13.1'])
