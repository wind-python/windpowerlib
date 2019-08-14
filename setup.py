import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='windpowerlib',
      version='0.2.0dev',
      description='Creating time series of wind power plants.',
      url='http://github.com/wind-python/windpowerlib',
      author='oemof developer group',
      author_email='windpowerlib@rl-institut.de',
      license=None,
      packages=['windpowerlib'],
      package_data={
          'windpowerlib': [os.path.join('data', '*.csv'),
                           os.path.join('oedb', '*.csv')]},
      long_description=read('README.rst'),
      zip_safe=False,
      install_requires=['pandas >= 0.20.0, < 0.26',
                        'requests < 3.0'],
      extras_require={
          'dev': ['pytest', 'jupyter', 'sphinx_rtd_theme', 'nbformat',
                  'numpy']})
