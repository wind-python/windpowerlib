"""
The ``turbine_cluster`` module is under development and is not working yet.

"""
# TODO: desciption

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np
#from windpowerlib import wind_turbine


def gaussian_distribution(function_variable, standard_deviation, median=0):
    r"""
    Normal distribution or gaussian distribution


    Parameters
    ----------
    function_variable : 
        Variable of the gaussian distribution.
    standard_deviation : float
        Standard deviation of the guassian distribution.
    median : float
        Defines the offset of the gaussian distribution function. Default: 0.
        TODO: figure could be added for explanation

    Returns
    -------
    

    """
    return (1 / (standard_deviation * np.sqrt(2 * np.pi)) *
            np.exp(-0.5 * ((function_variable - median) / standard_deviation)**2))


#def smooth_p_curve(p_values):
#    r"""
#
#
#    Parameters
#    ----------
#    p_values : pandas.Series
#        Power curve of the wind turbine.
#        Indices are the wind speeds of the power curve in m/s.
#
#
#    Returns
#    -------
#
#
#    """
#    return


#class WindPark(object):
#    def __init__(self, wind_turbines, p_curve=None):
#        self.wind_turbines = wind_turbines
#        self.p_curve = self.wind_park_p_curve()
#
#    def wind_park_p_curve(self):
#        print(self.wind_turbines[0].p_values)
#        print(self.wind_turbines[1].p_values)
#        p_curve = np.sum([self.wind_turbines[i].p_values
#                          for i in range(len(self.wind_turbines))], axis=0)
#        return p_curve
#
#enerconE126 = {
#    'turbine_name': 'ENERCON E 126 7500',  # turbine name as in register
#    'hub_height': 135,  # in m
#    'rotor_diameter': 127  # in m
#}
#
#vestasV90 = {
#    'hub_height': 105,
#    'rotor_diameter': 90,
#    'turbine_name': 'VESTAS V 90 3000'}
#
## Initialize WindTurbine objects
#e126 = wind_turbine.WindTurbine(**enerconE126)
#v90 = wind_turbine.WindTurbine(**vestasV90)
#
#
#def wind_park_p_curve(wind_turbines):
#    print(wind_turbines[0].p_values)
#    print(wind_turbines[1].p_values)
#    p_curve = np.sum([wind_turbines[i].p_values
#                      for i in range(len(wind_turbines))], axis=0)
#    return p_curve
#
## park = WindPark([e126, v90])
##
## print(park)
## p_curve = wind_park_p_curve([e126, v90])
## print(p_curve)
#
