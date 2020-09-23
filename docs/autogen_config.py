#!/usr/bin/env python
"""
autogen_config.py

Creates config_options.rst, a Sphinx documentation source file.
Documents the options that may be set in nbconvert's configuration file,
jupyter_nbconvert_config.py.

"""
import os.path
from nbconvert.nbconvertapp import NbConvertApp

header = """\

.. This is an automatically generated file.
.. do not modify by hand.

Configuration options
=====================

Configuration options may be set in a file, ``~/.jupyter/jupyter_nbconvert_config.py``,
or at the command line when starting nbconvert, i.e. ``jupyter nbconvert --Application.log_level=10``.

The most specific setting will always be used. For example, the LatexExporter
and the HTMLExporter both inherit from TemplateExporter. With the following config

.. code-block:: python

    c.TemplateExporter.exclude_input_prompt = False # The default
    c.PDFExporter.exclude_input_prompt = True

input prompts will not appear when converting to PDF, but they will appear when
exporting to HTML.

CLI Flags and Aliases
---------------------

When using Nbconvert from the command line, a number of aliases and flags are
defined as shortcuts to configuration options for convience.

"""

try:
    indir = os.path.dirname(__file__)
except NameError:
    indir = os.path.dirname(os.getcwd())
destination = os.path.join(indir, 'source/config_options.rst')

with open(destination, 'w') as f:
    app = NbConvertApp()
    f.write(header)
    f.write(app.document_flag_help())
    f.write(app.document_alias_help())
    f.write(app.document_config_options())
