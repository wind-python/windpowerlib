
=========================================
 Model Description
=========================================

So far only two simple models are provided but there will improvements and a larger variety in future version hopefully with the help of the github community.


Wind Model
~~~~~~~~~~

The wind model is a simple model based on the cp-values of a specific type of a wind turbine. The cp-values are provided by the manufacturer of the wind turbine as a list of cp-values for discrete wind speeds in steps of 0.5 or 1 m/s. The feedinlib makes an linear interpolation of these values to get a continuous cp-curve over the wind speeds.

.. math::

    P_{wpp}=\frac{1}{8}\cdot\rho_{air,hub}\cdot d_{rotor}^{2}\cdot\pi\cdot v_{wind,hub}^{3}\cdot cp\left(v_{wind,hub}\right)
    
with :math:`d_{rotor}` the diameter of the rotor in meters, :math:`\rho_{air,hub}` the density of the air at hub height, :math:`v_{wind,hub}` the wind speed at hub height and :math:`cp` the cp-values against the wind speed.
    
The wind speed at hub height is determined by the following equation, assuming a logarithmic wind profile.

.. math::
    
    v_{wind,hub}=v_{wind,data}\cdot\frac{\ln\left(\frac{h_{hub}}{z_{0}}\right)}{\ln\left(\frac{h_{wind,data}}{z_{0}}\right)}
    
with :math:`v_{wind,hub}` the wind speed at the height of the weather model or measurement, :math:`h_{hub}` the height of the hub and :math:`h_{wind,data}` the height of the wind speed measurement or the height of the wind speed within the weather model. 
    
The density of the air is calculated assuming a temperature gradient of -6.5 K/km and a pressure gradient of -1/8 hPa/m.
    
.. math::
  
    T_{hub}=T_{air, data}-0.0065\cdot\left(h_{hub}-h_{T,data}\right)
    
with :math:`T_{air, data}` the temperature at the height of the weather model or measurement, :math:`h_{hub}` the height of the hub and :math:`h_{T,Data}` the height of temperature measurement or the height of the temperature within the weather model.   
    
.. math::
        
    \rho_{air,hub}=\left(p_{data}/100-\left(h_{hub}-h_{p,data}\right)*\frac{1}{8}\right)/\left(2.8706\cdot T_{hub}\right)
    
with :math:`p_{data}` the pressure at the height of the weather model or measurement, :math:`T_{hub}` the temperature of the air at hub height, :math:`h_{hub}` the height of the hub and :math:`h_{p,data}` the height of pressure measurement or the height of pressure within the weather model.

Weather Data
~~~~~~~~~~~~

The weather data manly used by the oemof developing group is the coastDat2 of the Helmholtz-Zentrum Geesthacht 

http://wiki.coast.hzg.de/pages/viewpage.action?pageId=4751533

Due to licence problems we are not allowed to ship the dataset with the windpowerlib. Please contact the Helmholtz-Zentrum Geesthacht (HZG), the data set for Europe might be free for non commercial use.