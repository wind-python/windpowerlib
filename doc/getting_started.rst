~~~~~~~~~~~~~~~~~~~~~~
Getting started
~~~~~~~~~~~~~~~~~~~~~~

Introduction
=============

The windpowerlib is a library that provides a set of functions and classes to calculate the power output of wind turbines. It was originally part of the 
`feedinlib <https://github.com/oemof/feedinlib>`_ (windpower and photovoltaic) but was taken out to build up a community concentrating on wind power models.

For a quick start see the :ref:`examplereference-label` section.


Documentation
==============

Full documentation can be found at `readthedocs <http://windpowerlib.readthedocs.org>`_.

Use the `project site <http://readthedocs.org/projects/windpowerlib>`_ of readthedocs to choose the version of the documentation. 
Go to the `download page <http://readthedocs.org/projects/windpowerlib/downloads/>`_ to download different versions and formats (pdf, html, epub) of the documentation.


Installation
============

If you have a working Python 3 environment, use pypi to install the latest windpowerlib version. We highly recommend to use virtual environments.

::

    pip install windpowerlib

The windpowerlib is designed for Python 3 and tested on Python >= 3.5.
Please see the `installation page <http://oemof.readthedocs.io/en/stable/installation_and_setup.html>`_ of the oemof documentation for complete instructions on how to install python and a virtual environment on your operating system.

Optional Packages
~~~~~~~~~~~~~~~~~

To see the plots of the windpowerlib example in the :ref:`examplereference-label` section you should `install the matplotlib package <http://matplotlib.org/users/installing.html>`_.
Matplotlib can be installed using pip3 though some Linux users reported that it is easier and more stable to use the pre-built packages of your Linux distribution.


.. _examplereference-label:

Examples and basic usage
=========================

The basic usage of the windpowerlib is shown in the :ref:`modelchain_example <modelchain_example_notebook.ipynb>`. The presented example is available as jupyter notebook and python script. You can download them along with example weather data:

 * :download:`ModelChain example (Python script) <../example/modelchain_example.py>`
 * :download:`ModelChain example (Jupyter notebook) <../example/modelchain_example.ipynb>`
 * :download:`Example data file <../example/weather.csv>`

To run the examples you first have to install the windpowerlib. To run the notebook you also need to install notebook using pip3. To launch jupyter notebook type ``jupyter notebook`` in terminal.
This will open a browser window. Navigate to the directory containing the notebook to open it. See the jupyter notebook quick start guide for more information on `how to install <http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/install.html>`_ and
`how to run <http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/execute.html>`_ jupyter notebooks.

Further functionalities, like the modelling of wind farms and wind turbine clusters, are shown in a second example. As the ModelChain example it is available as jupyter notebook and as python script. The weather data in this example is the same as in the example above.

 * :download:`TurbineClusterModelChain example (Python script) <../example/turbine_cluster_modelchain_example.py>`
 * :download:`TurbineClusterModelChain example (Jupyter notebook) <../example/turbine_cluster_modelchain_example.ipynb>`
 * :download:`Example data file <../example/weather.csv>`

Contributing
==============

We are warmly welcoming all who want to contribute to the windpowerlib. If you are interested in wind models and want to help improving the existing model do not hesitate to contact us.

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

Copyright (C) 2017 oemof developing group

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.