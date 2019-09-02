import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='windpowerlib',
      version='0.1.3',
      description='Creating time series of wind power plants.',
      url='http://github.com/wind-python/windpowerlib',
      author='oemof developer group',
      author_email='windpowerlib@rl-institut.de',
      license=None,
      packages=['windpowerlib'],
      package_data={
          'windpowerlib': [os.path.join('data', '*.csv')]},
      long_description=read('README.rst'),
      long_description_content_type='text/rst',
      zip_safe=False,
      install_requires=['pandas >= 0.19.1, < 0.26',
                        'requests < 3.0'],
      extras_require={
          'dev': ['pytest', 'jupyter', 'sphinx_rtd_theme', 'nbformat']})
