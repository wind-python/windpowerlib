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
