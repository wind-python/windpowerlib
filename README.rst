.. image:: https://travis-ci.org/wind-python/windpowerlib.svg?branch=dev
    :target: https://travis-ci.org/wind-python/windpowerlib
.. image:: https://coveralls.io/repos/github/wind-python/windpowerlib/badge.svg?branch=dev
    :target: https://coveralls.io/github/wind-python/windpowerlib?branch=dev
.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.824267.svg
   :target: https://doi.org/10.5281/zenodo.824267
.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/wind-python/windpowerlib/dev?filepath=example
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/lgtm/grade/python/g/wind-python/windpowerlib.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/wind-python/windpowerlib/context:python
   
Introduction
=============

The windpowerlib is a library that provides a set of functions and classes to calculate the power output of wind turbines. It was originally part of the 
`feedinlib <https://github.com/oemof/feedinlib>`_ (windpower and photovoltaic) but was taken out to build up a community concentrating on wind power models.

For a quick start see the `Examples and basic usage <http://windpowerlib.readthedocs.io/en/stable/getting_started.html#examplereference-label>`_ section.


Documentation
==============

Full documentation can be found at `readthedocs <https://windpowerlib.readthedocs.io/en/stable/>`_.

Use the `project site <http://readthedocs.org/projects/windpowerlib>`_ of readthedocs to choose the version of the documentation. 
Go to the `download page <http://readthedocs.org/projects/windpowerlib/downloads/>`_ to download different versions and formats (pdf, html, epub) of the documentation.


Installation
============

If you have a working Python 3 environment, use pypi to install the latest windpowerlib version:

::

    pip install windpowerlib

The windpowerlib is designed for Python 3 and tested on Python >= 3.5. We highly recommend to use virtual environments.
Please see the `installation page <http://oemof.readthedocs.io/en/stable/installation_and_setup.html>`_ of the oemof documentation for complete instructions on how to install python and a virtual environment on your operating system.

Optional Packages
~~~~~~~~~~~~~~~~~

To see the plots of the windpowerlib example in the `Examples and basic usage <http://windpowerlib.readthedocs.io/en/stable/getting_started.html#examplereference-label>`_ section you should `install the matplotlib package <http://matplotlib.org/users/installing.html>`_.
Matplotlib can be installed using pip:

::

    pip install matplotlib

.. _examplereference-label:

Examples and basic usage
=========================

The simplest way to run the example notebooks without installing windpowerlib is to click `here <https://mybinder.org/v2/gh/wind-python/windpowerlib/dev?filepath=example>`_ and open them with Binder.

The basic usage of the windpowerlib is shown in the `ModelChain example <http://windpowerlib.readthedocs.io/en/stable/modelchain_example_notebook.html>`_ that is available as jupyter notebook and python script:

* `ModelChain example (Python script) <https://raw.githubusercontent.com/wind-python/windpowerlib/master/example/modelchain_example.py>`_
* `ModelChain example (Jupyter notebook) <https://raw.githubusercontent.com/wind-python/windpowerlib/master/example/modelchain_example.ipynb>`_

To run the example you need the example weather and turbine data used:

* `Example weather data file <https://raw.githubusercontent.com/wind-python/windpowerlib/master/example/weather.csv>`_
* `Example power curve data file <https://raw.githubusercontent.com/wind-python/windpowerlib/master/example/data/example_power_curves.csv>`_
* `Example power coefficient curve data file <https://raw.githubusercontent.com/wind-python/windpowerlib/master/example/data/example_power_coefficient_curves.csv>`_
* `Example nominal power data file <https://raw.githubusercontent.com/wind-python/windpowerlib/master/example/data/example_turbine_data.csv>`_

To run the examples locally you have to install windpowerlib. To run the notebook you also need to install `notebook` using pip3. To launch jupyter notebook type ``jupyter notebook`` in the terminal.
This will open a browser window. Navigate to the directory containing the notebook to open it. See the jupyter notebook quick start guide for more information on `how to install <http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/install.html>`_ and
`how to run <http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/execute.html>`_ jupyter notebooks. In order to reproduce the figures in a notebook you need to install `matplotlib`.

Further functionalities, like the modelling of wind farms and wind turbine clusters, are shown in the `TurbineClusterModelChain example <http://windpowerlib.readthedocs.io/en/stable/turbine_cluster_modelchain_example_notebook.html>`_. As the ModelChain example it is available as jupyter notebook and as python script. The weather and turbine datadata used in this example is the same as in the example above.

* `TurbineClusterModelChain example (Python script) <https://raw.githubusercontent.com/wind-python/windpowerlib/master/example/turbine_cluster_modelchain_example.py>`_
* `TurbineClusterModelChain example (Jupyter notebook) <https://raw.githubusercontent.com/wind-python/windpowerlib/master/example/turbine_cluster_modelchain_example.ipynb>`_

You can also look at the examples in the `Examples section <http://windpowerlib.readthedocs.io/en/stable/examples.html>`_.

Wind turbine data
==================

The windpowerlib provides `wind turbine data <https://github.com/wind-python/windpowerlib/tree/master/windpowerlib/oedb>`_
(power curves, hub heights, etc.) for a large set of wind turbines. Have a look at the `example <http://windpowerlib.readthedocs.io/en/stable/modelchain_example_notebook.html#Initialize-wind-turbine>`_ on how
to use this data in your simulations.

The dataset is hosted and maintained on the `OpenEnergy database <https://openenergy-platform.org/dataedit/>`_ (oedb).
To update your local files with the latest version of the `oedb turbine library <https://openenergy-platform.org/dataedit/view/supply/wind_turbine_library>`_ you can execute the following in your python console:

.. code:: python

  from windpowerlib.wind_turbine import load_turbine_data_from_oedb
  load_turbine_data_from_oedb()

We would like to encourage anyone to contribute to the turbine library by adding turbine data or reporting errors in the data.
See `here <https://github.com/OpenEnergyPlatform/data-preprocessing/issues/28>`_ for more information on how to contribute.

Contributing
==============

We are warmly welcoming all who want to contribute to the windpowerlib. If you are interested in wind models and want to help improving the existing model do not hesitate to contact us via github or email (windpowerlib@rl-institut.de).

Clone: https://github.com/wind-python/windpowerlib and install the cloned repository using pip:

.. code:: bash

  pip install -e /path/to/the/repository

As the windpowerlib started with contributors from the `oemof developer group <https://github.com/orgs/oemof/teams/oemof-developer-group>`_ we use the same
`developer rules <http://oemof.readthedocs.io/en/stable/developing_oemof.html>`_.

**How to create a pull request:**

* `Fork <https://help.github.com/articles/fork-a-repo>`_ the windpowerlib repository to your own github account.
* Change, add or remove code.
* Commit your changes.
* Create a `pull request <https://guides.github.com/activities/hello-world/>`_ and describe what you will do and why.
* Wait for approval.

**Generally the following steps are required when changing, adding or removing code:**

* Add new tests if you have written new functions/classes.
* Add/change the documentation (new feature, API changes ...).
* Add a whatsnew entry and your name to Contributors.
* Check if all tests still work by simply executing pytest in your windpowerlib directory:

.. role:: bash(code)
   :language: bash

.. code:: bash

    pytest

Citing the windpowerlib
========================

We use the zenodo project to get a DOI for each version. `Search zenodo for the right citation of your windpowerlib version <https://zenodo.org/search?page=1&size=20&q=windpowerlib>`_.

License
============

Copyright (c) 2019 oemof developer group

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
