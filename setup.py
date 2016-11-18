# -*- coding: utf-8 -*-
"""
@author: uwe
"""

import sys
from setuptools import setup

setup(name='windpowerlib',
      version='0.0.3',
      description='Creating time series from wind power plants.',
      url='http://github.com/wind-python/windpowerlib',
      author='oemof developing group',
      author_email='mail',
      license=None,
      packages=['windpowerlib'],
      zip_safe=False,
      install_requires=['numpy >= 1.7.0',
                        'pandas >= 0.13.1',
                        'requests'])
