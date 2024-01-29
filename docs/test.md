HistoSlider Application
=============================

This repository contains a code for QT for Python based application.

Getting started
---------------

New installation mechanics (see: https://stackoverflow.com/questions/28509965/setuptools-development-requirements):

    pip install -e .[dev] .

Resources and translations
--------------------------

In order to ease the development process, the Qt Creator project
`histoslider.pro` is provided. You can open it to edit the UI files or to manage
resources. Translations can be edited using Qt Linguist, part of the Qt
SDK. In order to build the translations, you will need to have the
`lrelease` command on your `PATH` or set its full path to the
`LRELEASE_BIN` environment variable. UI files, translations and
resources can be built like this:

    python setup.py build_res

Note that this command is automatically run before running `sdist` and
`bdist_app` commands.

Compiled application
--------------------

You can generate a *compiled* application so that end-users do not need
to install anything. You can tweak some settings on the `histoslider.spec` file.
It can be generated like this:

    python setup.py bdist_app

Linting
-------

Flake8 is a great tool to check for style issues, unused imports and
similar stuff. You can tweak `.flake8` to ignore certain types of
errors, increase the maximum line length, etc. You can run it like this:

    flake8 app
