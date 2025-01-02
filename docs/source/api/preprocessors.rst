Preprocessors
=============

.. module:: nbconvert.preprocessors
   :noindex:

.. seealso::

   :doc:`/config_options`
     Configurable options for the nbconvert application

.. autoclass:: Preprocessor

    .. automethod:: __init__

    .. automethod:: preprocess

    .. automethod:: preprocess_cell

Specialized preprocessors
-------------------------

Converting and extracting figures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ConvertFiguresPreprocessor

.. autoclass:: SVG2PDFPreprocessor

.. autoclass:: ExtractOutputPreprocessor

Converting text
~~~~~~~~~~~~~~~

.. autoclass:: LatexPreprocessor

.. autoclass:: HighlightMagicsPreprocessor

.. autoclass:: NumberedHeadingsPreprocessor

Metadata and header control
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ClearMetadataPreprocessor

.. autoclass:: CSSHTMLHeaderPreprocessor

Removing/Manipulating cells, inputs, and outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ClearOutputPreprocessor

.. autoclass:: CoalesceStreamsPreprocessor

.. autoclass:: RegexRemovePreprocessor

.. autoclass:: TagRemovePreprocessor

Executing Notebooks
~~~~~~~~~~~~~~~~~~~

.. autoclass:: ExecutePreprocessor
    :members:

.. autoclass:: CellExecutionError
