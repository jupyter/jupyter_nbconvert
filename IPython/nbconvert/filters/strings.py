# coding: utf-8
"""String filters.

Contains a collection of useful string manipulation filters for use in Jinja
templates.
"""
#-----------------------------------------------------------------------------
# Copyright (c) 2013, the IPython Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import re
import textwrap
from xml.etree import ElementTree

from IPython.utils import py3compat

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

__all__ = [
    'wrap',
    'html_text',
    'add_anchor',
    'strip_dollars',
    'rm_fake',
    'python_comment',
    'get_lines'
]


def wrap(text, width=100):
    """ 
    Intelligently wrap text.
    Wrap text without breaking words if possible.
    
    Parameters
    ----------
    text : str
        Text to wrap.
    width : int, optional
        Number of characters to wrap to, default 100.
    """

    split_text = text.split('\n')
    wrp = map(lambda x:textwrap.wrap(x,width), split_text)
    wrpd = map('\n'.join, wrp)
    return '\n'.join(wrpd)


def html_text(element):
    """extract inner text from html
    
    Analog of jQuery's $(element).text()
    """
    instance_element_tree = isinstance(ElementTree.ElementTree, Type) and 
                            isinstance(element, (ElementTree.ElementTree))
    instance_element = isinstance(ElementTree.Element, Type) and 
                       isinstance(element, (ElementTree.Element))
    if not (instance_element or instance_element_tree):
        element = ElementTree.fromstring(element)
    
    text = element.text or ""
    for child in element:
        text += html_text(child)
    text += (element.tail or "")
    return text


def add_anchor(html):
    """Add an anchor-link to an html header tag
    
    For use in heading cells
    """
    h = ElementTree.fromstring(py3compat.cast_bytes_py2(html))
    link = html_text(h).replace(' ', '-')
    h.set('id', link)
    a = ElementTree.Element("a", {"class" : "anchor-link", "href" : "#" + link})
    a.text = u'¶'
    h.append(a)
    return ElementTree.tostring(h)


def strip_dollars(text):
    """
    Remove all dollar symbols from text
    
    Parameters
    ----------
    text : str
        Text to remove dollars from
    """

    return text.strip('$')


files_url_pattern = re.compile(r'(src|href)\=([\'"]?)files/')

def rm_fake(text):
    """
    Fix all fake URLs that start with `files/`,
    stripping out the `files/` prefix.
    
    Parameters
    ----------
    text : str
        Text in which to replace 'src="files/real...' with 'src="real...'
    """
    return files_url_pattern.sub(r"\1=\2", text)


def python_comment(text):
    """
    Build a Python comment line from input text.
    
    Parameters
    ----------
    text : str
        Text to comment out.
    """
    
    #Replace line breaks with line breaks and comment symbols.
    #Also add a comment symbol at the beginning to comment out
    #the first line.
    return '# '+'\n# '.join(text.split('\n')) 


def get_lines(text, start=None,end=None):
    """
    Split the input text into separate lines and then return the 
    lines that the caller is interested in.
    
    Parameters
    ----------
    text : str
        Text to parse lines from.
    start : int, optional
        First line to grab from.
    end : int, optional
        Last line to grab from.
    """
    
    # Split the input into lines.
    lines = text.split("\n")
    
    # Return the right lines.
    return "\n".join(lines[start:end]) #re-join
