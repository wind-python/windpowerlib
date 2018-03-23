"""
The ``wind_farm`` module contains the class WindFarm that implements
a wind farm in the windpowerlib and functions needed for the modelling of a
wind farm.

"""

__copyright__ = "Copyright oemof developer group"
__license__ = "GPLv3"

import numpy as np
import pandas as pd
import os

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None


class WindFarm(object):
    r"""
    Defines a standard set of wind farm attributes.

    Parameters
    ----------
    object_name : string
        Name of the wind farm.
    wind_turbine_fleet : list of dictionaries
        Wind turbines of wind farm. Dictionaries must have 'wind_turbine'
        (contains a :class:`~.wind_turbine.WindTurbine` object) and
        'number_of_turbines' (number of turbine type in wind farm) as keys.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.
    efficiency : Float or pd.DataFrame or Dictionary
        Efficiency of the wind farm. Either constant (float) or wind efficiency
        curve (pd.DataFrame or Dictionary) containing 'wind_speed' and
        'efficiency' columns/keys with wind speeds in m/s and the
        corresponding dimensionless wind farm efficiency. Default: None.

    Attributes
    ----------
    object_name : string
        Name of the wind farm.
    wind_turbine_fleet : list of dictionaries
        Wind turbines of wind farm. Dictionaries must have 'wind_turbine'
        (contains a :class:`~.wind_turbine.WindTurbine` object) and
        'number_of_turbines' (number of turbine type in wind farm) as keys.
    coordinates : list or None
        List of coordinates [lat, lon] of location for loading data.
        Default: None.
    efficiency : Float or pd.DataFrame or Dictionary
        Efficiency of the wind farm. Either constant (float) or wind efficiency
        curve (pd.DataFrame or Dictionary) containing 'wind_speed' and
        'efficiency' columns/keys with wind speeds in m/s and the
        corresponding dimensionless wind farm efficiency. Default: None.
    hub_height : float
        The calculated average hub height of the wind farm.
    installed_power : float
        Installed power of the wind farm.
    power_curve : pandas.DataFrame or None
        The calculated power curve of the wind farm.
    power_output : pandas.Series
        The calculated power output of the wind farm.
    """
    def __init__(self, object_name, wind_turbine_fleet, coordinates=None,
                 efficiency=None):

        self.object_name = object_name
        self.wind_turbine_fleet = wind_turbine_fleet
        self.coordinates = coordinates
        self.efficiency = efficiency

        self.hub_height = None
        self.installed_power = None
        self.power_curve = None
        self.power_output = None

    def mean_hub_height(self):
        r"""
        Calculates the mean power weighted hub height of a wind farm.

        Assigns the hub height to the wind farm object.

        Returns
        -------
        self

        Notes
        -----
        The following equation is used [1]_:
        .. math:: h_{WF} = e^{\sum\limits_{k}{ln(h_{WT,k})}
                           \frac{P_{N,k}}{\sum\limits_{k}{P_{N,k}}}}

        with:
            :math:`h_{WF}`: mean hub height of wind farm,
            :math:`h_{WT,k}`: hub height of the k-th wind turbine of a wind
            farm, :math:`P_{N,k}`: nominal power of the k-th wind turbine,

        References
        ----------
        .. [1]  Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
                 Windenergieeinspeisung für wetterdatenbasierte
                 Windleistungssimulationen". Universität Kassel, Diss., 2016,
                 p. 35

        """
        self.hub_height = np.exp(
            sum(np.log(wind_dict['wind_turbine'].hub_height) *
                wind_dict['wind_turbine'].nominal_power *
                wind_dict['number_of_turbines']
                for wind_dict in self.wind_turbine_fleet) /
            self.get_installed_power())
        return self

    def get_installed_power(self):
        r"""
        Calculates the installed power of a wind farm.

        Returns
        -------
        float
            Installed power of the wind farm.

        """
        return sum(
            wind_dict['wind_turbine'].nominal_power *
            wind_dict['number_of_turbines']
            for wind_dict in self.wind_turbine_fleet)


def read_wind_efficiency_curve(curve_name='dena_mean', plot=False):
    r"""
    Reads the in `curve_name` specified wind efficiency curve.

    Parameters
    ----------
    curve_name : String
        Specifies the curve.
        Possibilities: 'dena_mean', 'knorr_mean', 'dena_extrem1',
        'dena_extreme2, 'knorr_extreme1', 'knorr_extreme2', 'knorr_extreme3'.
        Default: 'dena_mean'.
    plot : Boolean
        If True the wind efficiency curve is plotted. Default: False.

    Returns
    -------
    efficiency_curve : pd.DataFrame
        Wind efficiency curve. Contains 'wind_speed' and 'efficiency' columns
        with wind speed in m/s and wind farm efficiency (dimensionless).

    Notes
    -----
    The wind efficiency curves were calculated in the "Dena Netzstudie" and in
    the disseration of Kaspar Knorr. For more information see [1]_ and [2]_.

    References
    ----------
    .. [1] Kohler et.al.: "dena-Netzstudie II. Integration erneuerbarer
            Energien in die deutsche Stromversorgung im Zeitraum 2015 – 2020
            mit Ausblick 2025.", Deutsche Energie-Agentur GmbH (dena),
            Tech. rept., 2010, p. 101
    .. [2] Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 124

    """
    path = os.path.join(os.path.dirname(__file__), 'data',
                        'wind_efficiency_curves.csv')
    wind_efficiency_curves = pd.read_csv(path)
    wind_speed = pd.Series(np.arange(0, 25.5, 0.5))
    if 'dena' in curve_name:
        x_values = wind_efficiency_curves['x_dena']
    if 'knorr' in curve_name:
        x_values = wind_efficiency_curves['x_knorr']
    efficiency = np.interp(wind_speed, x_values,
                           wind_efficiency_curves['y_{}'.format(curve_name)])
    efficiency_curve = pd.DataFrame(data=[wind_speed.values,
                                          efficiency],).transpose()
    efficiency_curve.columns = ['wind_speed', 'efficiency']
    if plot:
        efficiency_curve.rename(columns={'wind_speed': 'wind speed m/s'},
                                inplace=True)
        efficiency_curve.set_index('wind speed m/s').plot(
            legend=False, title="Wind efficiency curve '{}'".format(
                curve_name))
        plt.ylabel('efficiency')
        plt.show()
    return efficiency_curve


def display_wind_efficiency_curves():
    r"""
    Plots or prints all efficiency curves available in the windpowerlib.

    Notes
    -----
    The wind efficiency curves were calculated in the "Dena Netzstudie" and in
    the disseration of Kaspar Knorr. For more information see [1]_ and [2]_.

    References
    ----------
    .. [1] Kohler et.al.: "dena-Netzstudie II. Integration erneuerbarer
            Energien in die deutsche Stromversorgung im Zeitraum 2015 – 2020
            mit Ausblick 2025.", Deutsche Energie-Agentur GmbH (dena),
            Tech. rept., 2010, p. 101
    .. [2] Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
             Windenergieeinspeisung für wetterdatenbasierte
             Windleistungssimulationen". Universität Kassel, Diss., 2016,
             p. 124

    """
    path = os.path.join(os.path.dirname(__file__), 'data',
                        'wind_efficiency_curves.csv')
    wind_efficiency_curves = pd.read_csv(path)
    curves_df = pd.DataFrame()
    for curve_name in [col.replace('y_', '') for
                       col in list(wind_efficiency_curves) if 'x_' not in col]:
        efficiency_curve = read_wind_efficiency_curve(
            curve_name).rename(
            columns={'efficiency': curve_name.replace('_', ' '),
                     'wind_speed': 'wind speed m/s'}).set_index(
                         'wind speed m/s')
        curves_df = pd.concat([curves_df, efficiency_curve], axis=1)
    knorr_df = curves_df[[column_name for column_name in curves_df if
                          'knorr' in column_name]]
    dena_df = curves_df[[column_name for column_name in curves_df if
                         'dena' in column_name]]
    if plt:
        fig, ax = plt.subplots()
        dena_df.plot(ax=ax, legend=True, marker='x', markersize=3)
        knorr_df.plot(ax=ax, legend=True, marker='o', markersize=3)
        plt.ylabel('Wind farm efficiency')
        plt.show()
#        fig.savefig('wind_eff_curves.pdf')
    else:
        print(dena_df)
        print(knorr_df)

if __name__ == "__main__":
    display_wind_efficiency_curves()
