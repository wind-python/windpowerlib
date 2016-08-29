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


Example
========
Download the .csv data and the example file and execute it:

https://github.com/wind-python/windpowerlib/tree/master/example


Basic Usage
===========

You need three steps to get a time series.

Warning
~~~~~~~
Be accurate with the units. In the example all units are given without a prefix.
 * pressure [Pa]
 * wind speed [m/s]
 * installed capacity [W]
 * nominal power [W]
 * area [m²]
 * temperature [°C]

You can also use kW instead of W but you have to make sure that all units are changed in the same way.

1. Initialise your Turbine or Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To initialise your specific turbine you need a dictionary that contains your basic parameters. 

The most import parameter is the name of the turbine to get technical parameters from the provided libraries. Use the *get_wind_pp_types* function to get a list of all available converter types.

.. code-block:: python

    from windpowerlib import basicmodel
    basicmodel.get_wind_pp_types()

The other parameters are related to location of the plant like diameter of the rotor or the hub height. The existing model needs the following parameters:

 * h_hub: height of the hub in meters
 * d_rotor: diameter of the rotor in meters
 * wind_conv_type: Name of the wind converter according to the list in the csv file

.. code:: python

    your_wind_turbine = basicmodel.SimpleWindTurbine(**your_parameter_set)

If you pass a valid model the nominal_power and the cp-values are read from a file. If you want to use your own converter you can pass your own cp-series and nominal power instead of the converter type. This can be done with a dictionary (as shown above) or directly.

.. code:: python

    your_wind_turbine = basicmodel.SimpleWindTurbine(cp_values=my_cp_values,
                                                     nominal_power=my_nominal_power,
                                                     d_rotor=my_d_rotor,
                                                     h_hub=my_h_hub)
       
2. Get your Feedin Time Series
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get your time series you have to pass a weather DataFrame (or dictionary) to your model.The DataFrame needs to have pressure, wind speed, temperature and the roughness length. The following names are used:

 * 'pressure'
 * 'temp_air'
 * 'v_wind'
 * 'z0'

In an additional dictionary the height of the weather data has to be defined. The example shows a dictionary for the coasdat2 weather data set:

.. code:: python  
     
    coastDat2 = {
        'dhi': 0,
        'dirhi': 0,
        'pressure': 0,
        'temp_air': 2,
        'v_wind': 10,
        'Z0': 0}
        
If your weather DataFrame has different column names you have to rename them. This can easily be done by using a conversion dictionary:

.. code:: python

    name_dc = {
        'your pressure data set': 'pressure',
        'your ambient temperature': 'temp_air',
        'your wind speed': 'v_wind',
        'your roughness length': 'z0'}
    
    your_weather_DataFrame.rename(columns=name_dc)
    
Now you can pass the weather data to the output method:
 
.. code:: python

    your_wind_turbine.turbine_power_output(weather=weather_df, data_height=coastDat2)
    
You will get the output of one wind_turbine in [W] if you followed the united recommendations from above.
