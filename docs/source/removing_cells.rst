Removing cells, inputs, or outputs
==================================

.. currentmodule:: nbconvert.preprocessors

When converting Notebooks into other formats, it is possible to
remove parts of a cell, or entire cells, using preprocessors.
The notebook will remain unchanged, but the outputs will have
certain pieces removed. The two primary ways for removal are:

    - Using cell tags
    - Using regular expressions

Removing pieces of cells using cell tags
----------------------------------------

The most straightforward way to control which pieces of cells are
removed is to use **cell tags**. These are single-string snippets of
metadata that are stored in each cells "tag" field. The
`TagRemovePreprocessor` can be used 
to remove inputs, outputs, or entire cells.

For example, here is a configuration that uses a different tag for
removing each part of a cell with the HTMLExporter. In this case,
we demonstrate using the nbconvert Python API.

.. code-block:: python

   from traitlets.config import Config
   import nbformat as nbf
   from nbconvert.exporters import HTMLExporter

   c = Config()

   # Configure our tag removal
   c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
   c.TagRemovePreprocessor.remove_all_outputs_tags = ('remove_output',)
   c.TagRemovePreprocessor.remove_input_tags = ('remove_input',)

   # Configure and run out exporter
   c.HTMLExporter.preprocessors = ["TagRemovePreprocessor"]
   HTMLExporter(config=c).from_filename("path/to/mynotebook.ipynb")

Removing cells using Regular Expressions on cell content
--------------------------------------------------------

Sometimes you'd rather remove cells based on their _content_ rather
than their tags. In this case, you can use the `RegexRemovePreprocessor`.

You initalize this preprocessor with a single ``patterns`` configuration, which
is a list of strings. For each cell, this preprocessor checks whether
the cell contents match any of the strings provided in ``patterns``.
If the contents match any of the patterns, the cell is removed from the notebook.

For example, executing the following command will convert a notebook to html
and remove cells containing only whitespace:

.. code-block:: bash

    jupyter nbconvert --RegexRemovePreprocessor.patterns="['\s*\Z']" mynotebook.ipynb

The command line argument sets the list of patterns to ``'\s*\Z'`` which matches
an arbitrary number of whitespace characters followed by the end of the string.

See https://regex101.com/ for an interactive guide to regular expressions
(make sure to select the python flavor). See https://docs.python.org/library/re.html
for the official regular expression documentation in python.

