"""Markdown filters

This file contains a collection of utility filters for dealing with
markdown within Jinja templates.
"""
# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
import re
import warnings

try:
    from .markdown_mistune import markdown2html_mistune
except ImportError as e:
    # store in variable for Python 3
    _mistune_import_error = e

    warnings.warn(
            "Conversion to other formats without mistune has been deprecated as of nbconvert 5.2."
            "It has been required for html export since at least nbconvert 4.0.",
            FutureWarning)
    def markdown2html_mistune(source):
        """mistune is unavailable, raise ImportError"""
        raise ImportError("markdown2html requires mistune: %s"
                          % _mistune_import_error)


from .pandoc import convert_pandoc


__all__ = [
    'markdown2html',
    'markdown2html_pandoc',
    'markdown2html_mistune',
    'markdown2latex',
    'markdown2rst',
    'markdown2asciidoc',
]

markdown2html = markdown2html_mistune

def markdown2latex(source, markup='markdown', extra_args=None):
    """
    Convert a markdown string to LaTeX via pandoc.

    This function will raise an error if pandoc is not installed.
    Any error messages generated by pandoc are printed to stderr.

    Parameters
    ----------
    source : string
      Input string, assumed to be valid markdown.
    markup : string
      Markup used by pandoc's reader
      default : pandoc extended markdown
      (see http://pandoc.org/README.html#pandocs-markdown)

    Returns
    -------
    out : string
      Output as returned by pandoc.
    """
    return convert_pandoc(source, markup, 'latex', extra_args=extra_args)


def markdown2html_pandoc(source, extra_args=None):
    """
    Convert a markdown string to HTML via pandoc.
    """
    
    warnings.warn(
            "markdown2html_pandoc has been deprecated as of nbconvert 5.2."
            "Using markdown2html_pandoc will not respect some configuration parameters."
            "If you wish to continue using pandoc for html conversion, please use"
            "convert_pandoc(source, 'markdown', 'html', extra_args=extra_args) directly.",
            FutureWarning)
   
    extra_args = extra_args or ['--mathjax']
    return convert_pandoc(source, 'markdown', 'html', extra_args=extra_args)


def markdown2asciidoc(source, extra_args=None):
    """Convert a markdown string to asciidoc via pandoc"""
    extra_args = extra_args or ['--atx-headers']
    asciidoc = convert_pandoc(source, 'markdown', 'asciidoc',
                              extra_args=extra_args)
    # workaround for https://github.com/jgm/pandoc/issues/3068
    if "__" in asciidoc:
        asciidoc = re.sub(r'\b__([\w \n-]+)__([:,.\n\)])', r'_\1_\2', asciidoc)
        # urls / links:
        asciidoc = re.sub(r'\(__([\w\/-:\.]+)__\)', r'(_\1_)', asciidoc)

    return asciidoc

def markdown2rst(source, extra_args=None):
    """
    Convert a markdown string to ReST via pandoc.

    This function will raise an error if pandoc is not installed.
    Any error messages generated by pandoc are printed to stderr.

    Parameters
    ----------
    source : string
      Input string, assumed to be valid markdown.

    Returns
    -------
    out : string
      Output as returned by pandoc.
    """
    return convert_pandoc(source, 'markdown', 'rst', extra_args=extra_args)
