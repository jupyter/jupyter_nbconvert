.. highlight:: none

Using the command line tool
===========================

``nbconvert`` can be run from the command line using::

  $ jupyter nbconvert --to FORMAT notebook.ipynb

For example, nbconvert will convert the Jupyter notebook file ``notebook.ipynb`` into the output
format given by the ``FORMAT`` string.

Default output format - HTML
----------------------------
nbconvert's default output format is HTML, and the ``--to`` argument may be
omitted::

  $ jupyter nbconvert notebook.ipynb

.. _supported_output:

Supported output formats
------------------------
The currently supported output formats are:

    - :ref:`HTML <convert_html>`,
    - :ref:`LaTeX <convert_latex>`,
    - :ref:`PDF <convert_pdf>`,
    - :ref:`WebPDF <convert_webpdf>`,
    - :ref:`Reveal.js HTML slideshow <convert_revealjs>`,
    - :ref:`Markdown <convert_markdown>`,
    - :ref:`Ascii <convert_ascii>`,
    - :ref:`reStructuredText <convert_rst>`,
    - :ref:`executable script <convert_script>`,
    - :ref:`notebook <convert_notebook>`.

Jupyter also provides a few templates for output formats. These can be
specified via an additional ``--template`` argument and are listed in the
sections below.

.. _convert_html:

HTML
~~~~
* ``--to html``

  HTML Export.  Note on backward compatibility:  Be aware that if you were using custom copies of the old 5.x
  template files (i.e. ``--template``), you will now need to use ``--template-file path/to/old/file.tpl``
  in order to use that file in compatibility mode as opposed to other options.

  - ``--template lab`` (default)

    A full static HTML render of the notebook.
    This looks very similar to the jupyter lab interactive view.

  - ``--template classic``

    Simplified HTML, using the classic jupyter look and feel.

.. _convert_latex:

LaTeX
~~~~~
* ``--to latex``

  Latex export.  This generates ``NOTEBOOK_NAME.tex`` file,
  ready for export.
  Images are output as .png files in a folder.

  - ``--template article`` (default)

    Latex article, derived from Sphinx's howto template.

  - ``--template report``

    Latex report, providing a table of contents and chapters.

  .. note::

    nbconvert uses pandoc_ to convert between various markup languages,
    so pandoc is a dependency when converting to latex or reStructuredText.

.. _convert_pdf:

PDF
~~~
* ``--to pdf``

  Generates a PDF via latex. Supports the same templates as ``--to latex``.

.. _convert_webpdf:

WebPDF
~~~~~~
* ``--to webpdf``

  Generates a PDF by first rendering to HTML, rendering the HTML Chromium headless, and
  exporting to PDF. This exporter supports the same templates as ``--to html``.

  The webpdf exporter requires the ``pyppeteer`` Chromium automation library, which
  can be installed via ``nbconvert[webpdf]``.

.. _convert_revealjs:

Reveal.js HTML slideshow
~~~~~~~~~~~~~~~~~~~~~~~~
* ``--to slides``

  This generates a Reveal.js HTML slideshow.

Running this slideshow requires a copy of reveal.js (version 3.x).

By default, this will include a script tag in the html that will directly load
reveal.js from a public CDN.

This means that if you include your slides on a webpage, they should work as
expected. However, some features (specifically, speaker notes & timers) will not
work on website because they require access to a local copy of reveal.js.

Speaker notes require a local copy of reveal.js. Then, you need to tell
``nbconvert`` how to find that local copy.

Timers only work if you already have speaker notes, but also require a local
https server. You can read more about this in ServePostProcessorExample_.

To make this clearer, let's look at an example of how to get speaker notes
working with a local copy of reveal.js: SlidesWithNotesExample_.

.. note::

  In order to designate a mapping from notebook cells to Reveal.js slides,
  from within the Jupyter notebook, select menu item
  View --> Cell Toolbar --> Slideshow. That will reveal a drop-down menu
  on the upper-right of each cell.  From it, one may choose from
  "Slide," "Sub-Slide", "Fragment", "Skip", and "Notes."  On conversion,
  cells designated as "skip" will not be included, "notes" will be included
  only in presenter notes, etc.

.. _SlidesWithNotesExample:

Example: creating slides w/ speaker notes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's suppose you have a notebook ``your_talk.ipynb`` that you want to convert
to slides. For this example, we'll assume that you are working in the same
directory as the notebook you want to convert (i.e., when you run ``ls .``,
``your_talk.ipynb`` shows up amongst the list of files).

First, we need a copy of reveal.js in the same directory as your slides. One
way to do this is to use the following commands in your terminal:

.. code-block:: shell

  git clone https://github.com/hakimel/reveal.js.git
  cd reveal.js
  git checkout 3.5.0
  cd ..

Then we need to tell nbconvert to point to this local copy. To do that we use
the ``--reveal-prefix`` command line flag to point to the local copy.

.. code-block:: shell

  jupyter nbconvert your_talk.ipynb --to slides --reveal-prefix reveal.js

This will create file ``your_talk.slides.html``, which you should be able to
access with ``open your_talk.slides.html``. To access the speaker notes, press
``s`` after the slides load and they should open in a new window.

Note: This does not enable slides that run completely offline. While you have a
local copy of reveal.js, by default, the slides need to access mathjax, require,
and jquery via a public CDN. Addressing this use case is an open issue and `PRs
<https://github.com/jupyter/nbconvert/pulls>`_ are always encouraged.

.. _ServePostProcessorExample:

Serving slides with an https server: ``--post serve``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have speaker notes working you may notice that your timers don't work.
Timers require a bit more infrastructure; you need to serve your local copy of
reveal.js from a local https server.

Fortunately, ``nbconvert`` makes this fairly straightforward through the use of
the ``ServePostProcessor``. To activate this server, we append the command line
flag ``--post serve`` to our call to nbconvert.

.. code-block:: shell

  jupyter nbconvert your_talk.ipynb --to slides --reveal-prefix reveal.js --post serve

This will run the server, which will occupy the terminal that you ran the
command in until you stop it. You can stop the server by pressing ``ctrl C``
twice.

.. _convert_markdown:

Markdown
~~~~~~~~
* ``--to markdown``

  Simple markdown output.  Markdown cells are unaffected,
  and code cells indented 4 spaces.
  Images are output as .png files in a folder.

.. _convert_ascii:

Ascii
~~~~~
* ``--to asciidoc``

  Ascii output.
  Images are output as .png files in a folder.

.. _convert_rst:

reStructuredText
~~~~~~~~~~~~~~~~
* ``--to rst``

  Basic reStructuredText output. Useful as a starting point for embedding
  notebooks in Sphinx docs.
  Images are output as .png files in a folder.

  .. note::

    nbconvert uses pandoc_ to convert between various markup languages,
    so pandoc is a dependency when converting to LaTeX or reStructuredText.

.. _convert_script:

Executable script
~~~~~~~~~~~~~~~~~
* ``--to script``

  Convert a notebook to an executable script.
  This is the simplest way to get a Python (or other language, depending on
  the kernel) script out of a notebook. If there were any magics in an
  Jupyter notebook, this may only be executable from a Jupyter session.

  For example, to convert a Julia notebook to a Julia executable script::

      jupyter nbconvert --to script my_julia_notebook.ipynb

.. _convert_notebook:

Notebook and preprocessors
~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``--to notebook``

  .. versionadded:: 3.0

  This doesn't convert a notebook to a different format *per se*,
  instead it allows the running of nbconvert preprocessors on a notebook,
  and/or conversion to other notebook formats. For example::

      jupyter nbconvert --to notebook --execute mynotebook.ipynb

This will open the notebook, execute it, capture new output, and save the
result in :file:`mynotebook.nbconvert.ipynb`. Specifying ``--inplace`` will
overwrite the input file instead of writing a new file. By default,
``nbconvert`` will abort conversion if any exceptions occur during
execution of a cell. If you specify ``--allow-errors`` (in addition to the
``--execute`` flag) then conversion will continue and the output from any
exception will be included in the cell output.

The following command::

      jupyter nbconvert --to notebook --nbformat 3 mynotebook

will create a copy of :file:`mynotebook.ipynb` in :file:`mynotebook.v3.ipynb`
in version 3 of the notebook format.

If you want to convert a notebook in-place, you can specify the output file
to be the same as the input file::

      jupyter nbconvert --to notebook mynb --output mynb

Be careful with that, since it will replace the input file.

.. note::

  nbconvert uses pandoc_ to convert between various markup languages,
  so pandoc is a dependency when converting to latex or reStructuredText.

.. _pandoc: https://pandoc.org/

The output file created by ``nbconvert`` will have the same base name as
the notebook and will be placed in the current working directory. Any
supporting files (graphics, etc) will be placed in a new directory with the
same base name as the notebook, suffixed with ``_files``::

  $ jupyter nbconvert notebook.ipynb
  $ ls
  notebook.ipynb   notebook.html    notebook_files/

For simple single-file output, such as html, markdown, etc.,
the output may be sent to standard output with::

  $ jupyter nbconvert --to markdown notebook.ipynb --stdout

Converting multiple notebooks
-----------------------------
Multiple notebooks can be specified from the command line for execution::

  $ jupyter nbconvert notebook*.ipynb
  $ jupyter nbconvert notebook1.ipynb notebook2.ipynb

A list in a configuration file may also be used. For example, in a config file ``mycfg.py``,
a list of notebooks can be specified:

.. code-block:: python

  c = get_config()
  c.NbConvertApp.notebooks = ["notebook1.ipynb", "notebook2.ipynb"]

and then executed using the command::

  $ jupyter nbconvert --config mycfg.py
