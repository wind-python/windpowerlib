"""
The ``wind_farm`` module contains the class WindFarm that implements
a wind farm in the windpowerlib and functions needed for the modelling of a
wind farm.

SPDX-FileCopyrightText: 2019 oemof developer group <contact@oemof.org>
SPDX-License-Identifier: MIT
"""
from windpowerlib import tools, power_curves, WindTurbine
import numpy as np
import pandas as pd
import logging
import warnings


class WindFarm(object):
    r"""
    Defines a standard set of wind farm attributes.

    Parameters
    ----------
    wind_turbine_fleet : :pandas:`pandas.DataFrame<frame>` or list(:class:`~windpowerlib.wind_turbine.WindTurbineGroup`)
        The wind turbine fleet specifies the turbine types in the wind farm and
        their corresponding number or total installed capacity. There are
        different options to provide the wind turbine fleet (see also examples
        below):

        * :pandas:`pandas.DataFrame<frame>` -
          DataFrame must have columns 'wind_turbine' containing a
          :class:`~.wind_turbine.WindTurbine` object and either
          'number_of_turbines' (number of wind turbines of the same turbine
          type in the wind farm, can be a float) or 'total_capacity'
          (installed capacity of wind turbines of the same turbine type in the
          wind farm).

        * list(:class:`~windpowerlib.wind_turbine.WindTurbineGroup`) -
          A :class:`~windpowerlib.wind_turbine.WindTurbineGroup` can be created
          from a :class:`~windpowerlib.wind_turbine.WindTurbine` using the
          :func:`~windpowerlib.wind_turbine.WindTurbine.to_group` method.

        * list(dict) -
          It is still possible to use a list of dictionaries (see example) but
          we recommend to use one of the other options above.

    efficiency : float or :pandas:`pandas.DataFrame<frame>` or None (optional)
        Efficiency of the wind farm. Provide as either constant (float) or
        power efficiency curve (pd.DataFrame) containing 'wind_speed' and
        'efficiency' columns with wind speeds in m/s and the corresponding
        dimensionless wind farm efficiency. Default: None.
    name : str (optional)
        Can be used as an identifier of the wind farm. Default: ''.

    Attributes
    ----------
    wind_turbine_fleet : :pandas:`pandas.DataFrame<frame>`
        Wind turbines of wind farm. DataFrame must have 'wind_turbine'
        (contains a :class:`~.wind_turbine.WindTurbine` object) and
        'number_of_turbines' (number of wind turbines of the same turbine type
        in the wind farm) as columns.
    efficiency : float or :pandas:`pandas.DataFrame<frame>` or None
        Efficiency of the wind farm. Either constant (float) power efficiency
        curve (pd.DataFrame) containing 'wind_speed' and 'efficiency'
        columns with wind speeds in m/s and the corresponding
        dimensionless wind farm efficiency. Default: None.
    name : str
        If set this is used as an identifier of the wind farm.
    hub_height : float
        The calculated mean hub height of the wind farm. See
        :py:func:`mean_hub_height` for more information.
    power_curve : :pandas:`pandas.DataFrame<frame>` or None
        The calculated power curve of the wind farm. See
        :py:func:`assign_power_curve` for more information.

    Examples
    --------
    >>> from windpowerlib import wind_farm
    >>> from windpowerlib import WindTurbine
    >>> import pandas as pd
    >>> enerconE126 = {
    ...    'hub_height': 135,
    ...    'rotor_diameter': 127,
    ...    'turbine_type': 'E-126/4200'}
    >>> e126 = WindTurbine(**enerconE126)
    >>> vestasV90 = {
    ...     'hub_height': 90,
    ...     'turbine_type': 'V90/2000',
    ...     'nominal_power': 2e6}
    >>> v90 = WindTurbine(**vestasV90)
    >>> # turbine fleet as DataFrame
    >>> wind_turbine_fleet = pd.DataFrame(
    ...     {'wind_turbine': [e126, v90],
    ...      'number_of_turbines': [6, None],
    ...      'total_capacity': [None, 3 * 2e6]})
    >>> example_farm = wind_farm.WindFarm(wind_turbine_fleet, name='my_farm')
    >>> print(example_farm.nominal_power)
    31200000.0
    >>> # turbine fleet as a list of WindTurbineGroup objects using the
    >>> # 'to_group' method.
    >>> wind_turbine_fleet = [e126.to_group(6),
    ...                       v90.to_group(total_capacity=3 * 2e6)]
    >>> example_farm = wind_farm.WindFarm(wind_turbine_fleet, name='my_farm')
    >>> print(example_farm.nominal_power)
    31200000.0
    >>> # turbine fleet as list of dictionaries (not recommended)
    >>> example_farm_data = {
    ...    'name': 'my_farm',
    ...    'wind_turbine_fleet': [{'wind_turbine': e126,
    ...                            'number_of_turbines': 6},
    ...                           {'wind_turbine': v90,
    ...                            'total_capacity': 3 * 2e6}]}
    >>> example_farm = wind_farm.WindFarm(**example_farm_data)
    >>> print(example_farm.nominal_power)
    31200000.0
    """

    def __init__(self, wind_turbine_fleet, efficiency=None, name="", **kwargs):

        self.wind_turbine_fleet = wind_turbine_fleet
        self.efficiency = efficiency
        self.name = name

        self.hub_height = None
        self._nominal_power = None
        self.power_curve = None

        self.check_and_complete_wind_turbine_fleet()

    def check_and_complete_wind_turbine_fleet(self):
        """
        Function to check wind turbine fleet user input.

        Besides checking if all necessary parameters to fully define the wind
        turbine fleet are provided, this function also fills in the
        number of turbines or total capacity of each turbine type and checks
        if they are consistent.

        """
        # convert list to dataframe if necessary
        if isinstance(self.wind_turbine_fleet, list):
            self.wind_turbine_fleet = pd.DataFrame(self.wind_turbine_fleet)

        # check wind turbines
        try:
            for turbine in self.wind_turbine_fleet["wind_turbine"]:
                if not isinstance(turbine, WindTurbine):
                    raise ValueError(
                        "Wind turbine must be provided as WindTurbine object "
                        "but was provided as {}.".format(type(turbine))
                    )
        except KeyError:
            raise KeyError(
                "Missing wind_turbine key/column in "
                "wind_turbine_fleet parameter."
            )

        # add columns for number of turbines and total capacity if they don't
        # yet exist
        if "number_of_turbines" not in self.wind_turbine_fleet.columns:
            self.wind_turbine_fleet["number_of_turbines"] = np.nan
        if "total_capacity" not in self.wind_turbine_fleet.columns:
            self.wind_turbine_fleet["total_capacity"] = np.nan

        # calculate number of turbines if necessary
        number_turbines_not_provided = self.wind_turbine_fleet[
            self.wind_turbine_fleet["number_of_turbines"].isnull()
        ]
        for ix, row in number_turbines_not_provided.iterrows():
            msg = (
                "Number of turbines of type {0} can not be deduced "
                "from total capacity. Please either provide "
                "`number_of_turbines` in the turbine fleet definition or "
                "set the nominal power of the wind turbine."
            )
            try:
                number_of_turbines = (
                    row["total_capacity"] / row["wind_turbine"].nominal_power
                )
                if np.isnan(number_of_turbines):
                    raise ValueError(msg.format(row["wind_turbine"]))
                else:
                    self.wind_turbine_fleet.loc[
                        ix, "number_of_turbines"
                    ] = number_of_turbines
            except TypeError:
                raise ValueError(msg.format(row["wind_turbine"]))

        # calculate total capacity if necessary and check that total capacity
        # and number of turbines is consistent if both are provided
        for ix, row in self.wind_turbine_fleet.iterrows():
            if np.isnan(row["total_capacity"]):
                try:
                    self.wind_turbine_fleet.loc[ix, "total_capacity"] = (
                        row["number_of_turbines"]
                        * row["wind_turbine"].nominal_power
                    )
                except TypeError:
                    raise ValueError(
                        "Total capacity of turbines of type {turbine} cannot "
                        "be deduced. Please check if the nominal power of the "
                        "wind turbine is set.".format(
                            turbine=row["wind_turbine"]
                        )
                    )
            else:
                if (
                    not abs(
                        row["total_capacity"]
                        - (
                            row["number_of_turbines"]
                            * row["wind_turbine"].nominal_power
                        )
                    )
                    < 1
                ):
                    self.wind_turbine_fleet.loc[ix, "total_capacity"] = (
                        row["number_of_turbines"]
                        * row["wind_turbine"].nominal_power
                    )
                    msg = (
                        "The provided total capacity of WindTurbine {0} has "
                        "been overwritten as it was not consistent with the "
                        "number of turbines provided for this type."
                    )
                    warnings.warn(
                        msg.format(row["wind_turbine"]),
                        tools.WindpowerlibUserWarning,
                    )

    def __repr__(self):
        if self.name != "":
            return "Wind farm: {name}".format(name=self.name)
        else:
            return "Wind farm with turbine fleet: [number, type]\n {}".format(
                self.wind_turbine_fleet.loc[
                    :, ["number_of_turbines", "wind_turbine"]
                ].values
            )

    @property
    def nominal_power(self):
        r"""
        The nominal power is the sum of the nominal power of all turbines.

        Returns
        -------
        float
            Nominal power of the wind farm in W.

        """
        if not self._nominal_power:
            self.nominal_power = self.wind_turbine_fleet.total_capacity.sum()
        return self._nominal_power

    @nominal_power.setter
    def nominal_power(self, nominal_power):
        self._nominal_power = nominal_power

    def mean_hub_height(self):
        r"""
        Calculates the mean hub height of the wind farm.

        The mean hub height of a wind farm is necessary for power output
        calculations with an aggregated wind farm power curve containing wind
        turbines with different hub heights. Hub heights of wind turbines with
        higher nominal power weigh more than others.
        After the calculations the mean hub height is assigned to the attribute
        :py:attr:`~hub_height`.

        Returns
        -------
        :class:`~.wind_farm.WindFarm`
            self

        Notes
        -----
        The following equation is used [1]_:

        .. math:: h_{WF} = e^{\sum\limits_{k}{ln(h_{WT,k})}
                           \frac{P_{N,k}}{\sum\limits_{k}{P_{N,k}}}}

        with:
            :math:`h_{WF}`: mean hub height of wind farm,
            :math:`h_{WT,k}`: hub height of the k-th wind turbine of a wind
            farm, :math:`P_{N,k}`: nominal power of the k-th wind turbine

        References
        ----------
        .. [1]  Knorr, K.: "Modellierung von raum-zeitlichen Eigenschaften der
                 Windenergieeinspeisung für wetterdatenbasierte
                 Windleistungssimulationen". Universität Kassel, Diss., 2016,
                 p. 35

        """
        self.hub_height = np.exp(
            sum(
                np.log(row["wind_turbine"].hub_height) * row["total_capacity"]
                for ix, row in self.wind_turbine_fleet.iterrows()
            )
            / self.nominal_power
        )
        return self

    def assign_power_curve(
        self,
        wake_losses_model="wind_farm_efficiency",
        smoothing=False,
        block_width=0.5,
        standard_deviation_method="turbulence_intensity",
        smoothing_order="wind_farm_power_curves",
        turbulence_intensity=None,
        **kwargs
    ):
        r"""
        Calculates the power curve of a wind farm.

        The wind farm power curve is calculated by aggregating the power curves
        of all wind turbines in the wind farm. Depending on the parameters the
        power curves are smoothed (before or after the aggregation) and/or a
        wind farm efficiency (power efficiency curve or constant efficiency) is
        applied after the aggregation.
        After the calculations the power curve is assigned to the attribute
        :py:attr:`~power_curve`.

        Parameters
        ----------
        wake_losses_model : str
            Defines the method for taking wake losses within the farm into
            consideration. Options: 'wind_farm_efficiency' or None.
            Default: 'wind_farm_efficiency'.
        smoothing : bool
            If True the power curves will be smoothed before or after the
            aggregation of power curves depending on `smoothing_order`.
            Default: False.
        block_width : float
            Width between the wind speeds in the sum of the equation in
            :py:func:`~.power_curves.smooth_power_curve`. Default: 0.5.
        standard_deviation_method : str
            Method for calculating the standard deviation for the Gauss
            distribution. Options: 'turbulence_intensity',
            'Staffell_Pfenninger'. Default: 'turbulence_intensity'.
        smoothing_order : str
            Defines when the smoothing takes place if `smoothing` is True.
            Options: 'turbine_power_curves' (to the single turbine power
            curves), 'wind_farm_power_curves'.
            Default: 'wind_farm_power_curves'.
        turbulence_intensity : float
            Turbulence intensity at hub height of the wind farm for power curve
            smoothing with 'turbulence_intensity' method. Can be calculated
            from `roughness_length` instead. Default: None.
        roughness_length : float (optional)
            Roughness length. If `standard_deviation_method` is
            'turbulence_intensity' and `turbulence_intensity` is not given
            the turbulence intensity is calculated via the roughness length.

        Returns
        -------
        :class:`~.wind_farm.WindFarm`
            self

        """
        # Check if all wind turbines have a power curve as attribute
        for turbine in self.wind_turbine_fleet["wind_turbine"]:
            if turbine.power_curve is None:
                raise ValueError(
                    "For an aggregated wind farm power curve "
                    + "each wind turbine needs a power curve "
                    + "but `power_curve` of '{}' is None.".format(turbine)
                )
        # Initialize data frame for power curve values
        df = pd.DataFrame()
        for ix, row in self.wind_turbine_fleet.iterrows():
            # Check if needed parameters are available and/or assign them
            if smoothing:
                if (
                    standard_deviation_method == "turbulence_intensity"
                    and turbulence_intensity is None
                ):
                    if (
                        "roughness_length" in kwargs
                        and kwargs["roughness_length"] is not None
                    ):
                        # Calculate turbulence intensity and write to kwargs
                        turbulence_intensity = tools.estimate_turbulence_intensity(
                            row["wind_turbine"].hub_height,
                            kwargs["roughness_length"],
                        )
                        kwargs["turbulence_intensity"] = turbulence_intensity
                    else:
                        raise ValueError(
                            "`roughness_length` must be defined for using "
                            + "'turbulence_intensity' as "
                            + "`standard_deviation_method` if "
                            + "`turbulence_intensity` is not given"
                        )
            # Get original power curve
            power_curve = pd.DataFrame(row["wind_turbine"].power_curve)
            # Editions to the power curves before the summation
            if smoothing and smoothing_order == "turbine_power_curves":
                power_curve = power_curves.smooth_power_curve(
                    power_curve["wind_speed"],
                    power_curve["value"],
                    standard_deviation_method=standard_deviation_method,
                    block_width=block_width,
                    **kwargs,
                )
            else:
                # Add value zero to start and end of curve as otherwise
                # problems can occur during the aggregation
                if power_curve.iloc[0]["wind_speed"] != 0.0:
                    power_curve = pd.concat(
                        [
                            pd.DataFrame(
                                data={"value": [0.0], "wind_speed": [0.0]}
                            ),
                            power_curve,
                        ],
                        join="inner",
                    )
                if power_curve.iloc[-1]["value"] != 0.0:
                    power_curve = pd.concat(
                        [
                            power_curve,
                            pd.DataFrame(
                                data={
                                    "wind_speed": [
                                        power_curve["wind_speed"].loc[
                                            power_curve.index[-1]
                                        ]
                                        + 0.5
                                    ],
                                    "value": [0.0],
                                }
                            ),
                        ],
                        join="inner",
                    )
            # Add power curves of all turbine types to data frame
            # (multiplied by turbine amount)
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        power_curve.set_index(["wind_speed"])
                        * row["number_of_turbines"]
                    ),
                ],
                axis=1,
            )
        # Aggregate all power curves
        wind_farm_power_curve = pd.DataFrame(
            df.interpolate(method="index").sum(axis=1)
        )
        wind_farm_power_curve.columns = ["value"]
        wind_farm_power_curve.reset_index(inplace=True)
        # Apply power curve smoothing and consideration of wake losses
        # after the summation
        if smoothing and smoothing_order == "wind_farm_power_curves":
            wind_farm_power_curve = power_curves.smooth_power_curve(
                wind_farm_power_curve["wind_speed"],
                wind_farm_power_curve["value"],
                standard_deviation_method=standard_deviation_method,
                block_width=block_width,
                **kwargs,
            )
        if wake_losses_model == "wind_farm_efficiency":
            if self.efficiency is not None:
                wind_farm_power_curve = power_curves.wake_losses_to_power_curve(
                    wind_farm_power_curve["wind_speed"].values,
                    wind_farm_power_curve["value"].values,
                    wind_farm_efficiency=self.efficiency,
                )
            else:
                msg = (
                    "If you use `wake_losses_model` '{model}' your WindFarm "
                    "needs an efficiency but `efficiency` is {eff}. \n\n"
                    "Failing farm:\n {farm}"
                )
                raise ValueError(
                    msg.format(
                        model=wake_losses_model, farm=self, eff=self.efficiency
                    )
                )
        self.power_curve = wind_farm_power_curve
        return self
