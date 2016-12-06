# -*- coding: utf-8 -*-
"""
@author: uwe
"""

import os
from setuptools import setup

setup(name='windpowerlib',
      version='0.0.4',
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
