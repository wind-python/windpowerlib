windpowerlib
==============

The windpowerlib is designed to calculate feedin time series of wind power plants. The windpowerlib is an out-take from the 
`feedinlib <https://github.com/oemof/feedinlib>`_ (windpower and pv) to build up a community concentrating on wind power models.

.. contents:: `Table of contents`
    :depth: 1
    :local:
    :backlinks: top

Introduction
============

Having weather data sets you can use the windpowerlib to calculate the electrical output of common wind turbines. 
Basic parameters for many manufacturers are provided with the library so that you can start directly using one of these parameter sets. Of course you are free to add your own parameter set.
For a quick start download the example weather data and basic example file and execute it:

https://github.com/wind-python/windpowerlib/tree/master/example

Documentation
==============

Full documentation can be found at `readthedocs <http://windpowerlib.readthedocs.org/en/latest/>`_. Use the project site of readthedocs to choose the version of the documentation. 

Contributing
==============

Clone/Fork: https://github.com/wind-python/windpowerlib

If you are interested in wind models and want to help improve the existing model do not hesitate to contact us.
As the windpowerlib started with contributors from the `oemof developer group <https://github.com/orgs/oemof/teams/oemof-developer-group>`_ we use the same 
`developer rules <http://oemof.readthedocs.io/en/stable/developing_oemof.html>`_.


Installation
============

If you have a working Python3 environment, use pypi to install the latest windpowerlib version.

::

    pip install windpowerlib

So far, the windpowerlib is mainly tested on python 3.4 but seems to work down to 2.7 
and for newer versions. Please see the `installation page <http://oemof.readthedocs.io/en/stable/installation_and_setup.html>`_ of the oemof documentation for complete instructions on how to install python on your operating system.

  
Optional Packages
~~~~~~~~~~~~~~~~~

To see the plots of the example file you should install the matplotlib package.

Matplotlib can be installed using pip3 but some Linux users reported that it is easier and more stable to use the pre-built packages of your Linux distribution.

http://matplotlib.org/users/installing.html

