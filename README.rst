The windpowerlib is designed to calculate feedin time series of wind power plants. The windpowerlib is an out-take from the feedinlib (windpower and pv) to build up a community concentrating on wind power models.

The windpowerlib is ready to use but may have some teething troubles. The used model is still very simple but we found some new contributors and the windpowerlib will improve soon. If you are interested in wind models and want to improve the existing model, publish an alternative model or extend it to wind farms do not hesitate to contact us.

.. contents:: `Table of contents`
    :depth: 1
    :local:
    :backlinks: top

Introduction
============

Having weather data sets you can use the windpowerlib to calculate the electrical output of common wind power plants. Basic parameters for many manufacturers are provided with the library so that you can start directly using one of these parameter sets. Of course you are free to add your own parameter set.

The cp-values for the wind turbines are provided by the Reiner Lemoine Institut and can be found here:

 * http://vernetzen.uni-flensburg.de/~git/cp_values.csv


Actual Release
~~~~~~~~~~~~~~

Download/Install: https://pypi.python.org/pypi/windpowerlib/

Documentation: http://pythonhosted.org/windpowerlib/

Developing Version
~~~~~~~~~~~~~~~~~~

Clone/Fork: https://github.com/wind-python/windpowerlib

Documentation: http://windpowerlib.readthedocs.org/en/latest/

As the windpowerlib started with contributors from the oemof developer group we use the same developer rules: http://oemof.readthedocs.io/en/stable/developer_notes.html


Installation
============

Using the windpowerlib
~~~~~~~~~~~~~~~~~~~~~~~

So far, the windpowerlib is mainly tested on python 3.4 but seems to work down
to 2.7.

Install the windpowerlib using pip3.

::

    pip3 install windpowerlib

Developing the Windpowerlib
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have push rights clone this repository to your local system.

::

    git clone git@github.com:oemof/windpower.git
    
If you do not have push rights, fork the project at github, clone your personal fork to your system and send a pull request.

If the project is cloned you can install it using pip3 with the -e flag. Using this installation, every change is applied directly.

::

    pip3 install -e <path/to/the/windpowerlib/root/dir>
    
  
Optional Packages
~~~~~~~~~~~~~~~~~

To see the plots of the example file one should install the matplotlib package.

Matplotlib can be installed using pip3 but some Linux users reported that it is easier and more stable to use the pre-built packages of your Linux distribution.

http://matplotlib.org/users/installing.html

