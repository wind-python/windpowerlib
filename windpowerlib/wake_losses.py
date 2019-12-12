"""
The ``wake_losses`` module contains functions for modelling wake losses by wind
efficiency curves (reduction of wind speed).

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
import numpy as np
import pandas as pd
import os


def reduce_wind_speed(wind_speed, wind_efficiency_curve_name='dena_mean'):
    r"""
    Reduces wind speed by a wind efficiency curve.

    The wind efficiency curves are provided in the windpowerlib and were
    calculated in the dena-Netzstudie II and in the work of Knorr
    (see [1]_ and [2]_).

    Parameters
    ----------
    wind_speed : :pandas:`pandas.Series<series>` or numpy.array
        Wind speed time series.
    wind_efficiency_curve_name : str
        Name of the wind efficiency curve. Use
        :py:func:`~.get_wind_efficiency_curve` to get all provided wind
        efficiency curves. Default: 'dena_mean'.

    Returns
    -------
    :pandas:`pandas.Series<series>` or np.array
        `wind_speed` reduced by wind efficiency curve.

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
    # Get wind efficiency curve
    wind_efficiency_curve = get_wind_efficiency_curve(
        curve_name=wind_efficiency_curve_name
    )
    # Reduce wind speed by wind efficiency
    reduced_wind_speed = wind_speed * np.interp(
        wind_speed,
        wind_efficiency_curve["wind_speed"],
        wind_efficiency_curve["efficiency"],
    )
    return reduced_wind_speed


def get_wind_efficiency_curve(curve_name="all"):
    r"""
    Reads wind efficiency curve(s) specified in `curve_name`.

    Parameters
    ----------
    curve_name : str or list(str)
        Specifies the curve. Use 'all' to get all curves in a MultiIndex
        DataFrame or one of the curve names to retrieve a single curve.
        Default: 'all'.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        Wind efficiency curve. Contains 'wind_speed' and 'efficiency' columns
        with wind speed in m/s and wind efficiency (dimensionless).
        If `curve_name` is 'all' or a list of strings a MultiIndex DataFrame is
        returned with curve names in the first level of the columns.

    Notes
    -----
    The wind efficiency curves were generated in the "Dena Netzstudie" [1]_ and
    in the work of Kaspar Knorr [2]_. The mean wind efficiency curve is an
    average curve from 12 wind farm distributed over Germany [1]_ or
    respectively an average from over 2000 wind farms in Germany [2]_. Curves
    with the appendix 'extreme' are wind efficiency curves of single wind farms
    that are extremely deviating from the respective mean wind efficiency
    curve. For more information see [1]_ and [2]_.

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

    Examples
    --------
    .. parsed-literal::
        # Example to plot all curves
        fig, ax=plt.subplots() /n
        df=get_wind_efficiency_curve(curve_name='all')
        for t in df.columns.get_level_values(0).unique():
            p=df[t].set_index('wind_speed')['efficiency']
            p.name=t
            ax=p.plot(ax=ax, legend=True)
        plt.show()

    """
    possible_curve_names = [
        "dena_mean",
        "knorr_mean",
        "dena_extreme1",
        "dena_extreme2",
        "knorr_extreme1",
        "knorr_extreme2",
        "knorr_extreme3",
    ]

    if curve_name == "all":
        curve_names = possible_curve_names
    elif isinstance(curve_name, str):
        curve_names = [curve_name]
    else:
        curve_names = curve_name

    efficiency_curve = pd.DataFrame()

    for curve_name in curve_names:
        if curve_name.split("_")[0] not in ["dena", "knorr"]:
            raise ValueError(
                "`curve_name` must be one of the following: "
                + "{} but is {}".format(possible_curve_names, curve_name)
            )
        path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "wind_efficiency_curves_{}.csv".format(curve_name.split("_")[0]),
        )
        # Read wind efficiency curves from file
        wind_efficiency_curves = pd.read_csv(path)
        # Raise error if wind efficiency curve specified in 'curve_name' does
        # not exist
        if curve_name not in list(wind_efficiency_curves):
            msg = (
                "Efficiency curve <{0}> does not exist. Must be one of the "
                "following: {1}."
            )
            raise ValueError(msg.format(curve_name, *possible_curve_names))

        # Get wind efficiency curve and rename column containing efficiency
        wec = wind_efficiency_curves[["wind_speed", curve_name]]
        if efficiency_curve.empty:
            efficiency_curve = pd.DataFrame(
                {
                    (curve_name, "wind_speed"): wec["wind_speed"],
                    (curve_name, "efficiency"): wec[curve_name],
                }
            )
        else:
            efficiency_curve[(curve_name, "wind_speed")] = wec["wind_speed"]
            efficiency_curve[(curve_name, "efficiency")] = wec[curve_name]
    if len(curve_names) == 1:
        return efficiency_curve[curve_names[0]]
    else:
        return efficiency_curve
