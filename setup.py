# -*- coding: utf-8 -*-
"""
@author: uwe
"""

import sys
from setuptools import setup

# check python version.
if not sys.version_info[:2] in ((2, 7), (3, 3), (3, 4)):
    sys.exit('%s requires Python 2.7, 3.3, or 3.4' % 'feedinlib')

setup(name='windpowerlib',
      version='0.0.1',
      description='Creating time series from wind power plants.',
      url='http://github.com/wind-python/windpowerlib',
      author='oemof developing group',
      author_email='mail',
      license=None,
      packages=['windpowerlib'],
      zip_safe=False,
      install_requires=['numpy >= 1.7.0',
                        'pandas >= 0.13.1',
                        'urllib5'])
