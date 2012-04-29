#!/usr/bin/env python
"""Convert IPython notebooks to other formats, such as ReST, and HTML.

Example:
  ./nbconvert.py --format html file.ipynb

Produces 'file.rst' and 'file.html', along with auto-generated figure files
called nb_figure_NN.png. To avoid the two-step process, ipynb -> rst -> html,
use '--format quick-html' which will do ipynb -> html, but won't look as
pretty.
"""
from __future__ import print_function

import codecs
import os
import pprint
import re
import subprocess
import sys

from IPython.external import argparse
from IPython.nbformat import current as nbformat
from IPython.utils.text import indent
from decorators import DocInherit

def remove_ansi(src):
    """Strip all ANSI color escape sequences from input string.

    Parameters
    ----------
    src : string

    Returns
    -------
    string
    """
    return re.sub(r'\033\[(0|\d;\d\d)m', '', src)

# Pandoc-dependent code
def markdown2latex(src):
    """Convert a markdown string to LaTeX via pandoc.

    This function will raise an error if pandoc is not installed.

    Any error messages generated by pandoc are printed to stderr.

    Parameters
    ----------
    src : string
      Input string, assumed to be valid markdown.

    Returns
    -------
    out : string
      Output as returned by pandoc.
    """
    p = subprocess.Popen('pandoc -f markdown -t latex'.split(),
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate(src)
    if err:
        print(err, file=sys.stderr)
    #print('*'*20+'\n', out, '\n'+'*'*20)  # dbg
    return out

# Cell converters


def rst_directive(directive, text=''):
    out = [directive, '']
    if text:
        out.extend([indent(text), ''])
    return out

# Converters for parts of a cell.


class ConversionException(Exception):
    pass


class Converter(object):
    default_encoding = 'utf-8'
    extension = str()
    figures_counter = 0
    infile = str()
    infile_dir = str()
    infile_root = str()
    files_dir = str()
    with_preamble = True
    user_preamble = None
    output = str()
        
    def __init__(self, infile):
        self.infile = infile
        self.infile_dir = os.path.dirname(infile)
        infile_root = os.path.splitext(infile)[0]
        files_dir = infile_root + '_files'
        if not os.path.isdir(files_dir):
            os.mkdir(files_dir)
        self.infile_root = infile_root
        self.files_dir = files_dir

    def dispatch(self, cell_type):
        """return cell_type dependent render method,  for example render_code
        """
        return getattr(self, 'render_' + cell_type, self.render_unknown)

    def convert(self):
        lines = []
        lines.extend(self.optional_header())
        for worksheet in self.nb.worksheets:
            for cell in worksheet.cells:
                conv_fn = self.dispatch(cell.cell_type)
                lines.extend(conv_fn(cell))
                lines.append('')
        lines.extend(self.optional_footer())
        return '\n'.join(lines)

    def render(self):
        "read, convert, and save self.infile"
        self.read()
        self.output = self.convert()
        return self.save()

    def read(self):
        "read and parse notebook into NotebookNode called self.nb"
        with open(self.infile) as f:
            self.nb = nbformat.read(f, 'json')

    def save(self, infile=None, encoding=None):
        "read and parse notebook into self.nb"
        if infile is None:
            infile = os.path.splitext(self.infile)[0] + '.' + self.extension
        if encoding is None:
            encoding = self.default_encoding
        with open(infile, 'w') as f:
            f.write(self.output.encode(encoding))
        return infile

    def optional_header(self):
        return []

    def optional_footer(self):
        return []

    def _new_figure(self, data, fmt):
        """Create a new figure file in the given format.

        Returns a path relative to the input file.
        """
        figname = '%s_fig_%02i.%s' % (self.infile_root, 
                                      self.figures_counter, fmt)
        self.figures_counter += 1
        fullname = os.path.join(self.files_dir, figname)

        # Binary files are base64-encoded, SVG is already XML
        if fmt in ('png', 'jpg', 'pdf'):
            data = data.decode('base64')
            fopen = lambda fname: open(fname, 'wb')
        else:
            fopen = lambda fname: codecs.open(fname, 'wb', self.default_encoding)
            
        with fopen(fullname) as f:
            f.write(data)
            
        return fullname

    def render_heading(self, cell):
        """convert a heading cell

        Returns list."""
        raise NotImplementedError

    def render_code(self, cell):
        """Convert a code cell

        Returns list."""
        raise NotImplementedError

    def render_markdown(self, cell):
        """convert a markdown cell

        Returns list."""
        raise NotImplementedError

    def render_pyout(self, output):
        """convert pyout part of a code cell

        Returns list."""
        raise NotImplementedError


    def render_pyerr(self, output):
        """convert pyerr part of a code cell

        Returns list."""
        raise NotImplementedError

    def _img_lines(self, img_file):
        """Return list of lines to include an image file."""
        # Note: subclasses may choose to implement format-specific _FMT_lines
        # methods if they so choose (FMT in {png, svg, jpg, pdf}).
        raise NotImplementedError

    def render_display_data(self, output):
        """convert display data from the output of a code cell

        Returns list.
        """
        lines = []

        for fmt in ['png', 'svg', 'jpg', 'pdf']:
            if fmt in output:
                img_file = self._new_figure(output[fmt], fmt)
                # Subclasses can have format-specific render functions (e.g.,
                # latex has to auto-convert all SVG to PDF first).
                lines_fun = getattr(self, '_%s_lines' % fmt, None)
                if not lines_fun:
                    lines_fun = self._img_lines
                lines.extend(lines_fun(img_file))

        return lines

    def render_stream(self, cell):
        """convert stream part of a code cell

        Returns list."""
        raise NotImplementedError

    def render_plaintext(self, cell):
        """convert plain text

        Returns list."""
        raise NotImplementedError

    def render_unknown(self, cell):
        """Render cells of unkown type

        Returns list."""
        raise NotImplementedError


class ConverterRST(Converter):
    extension = 'rst'
    heading_level = {1: '=', 2: '-', 3: '`', 4: '\'', 5: '.', 6: '~'}

    @DocInherit
    def render_heading(self, cell):
        marker = self.heading_level[cell.level]
        return ['{0}\n{1}\n'.format(cell.source, marker * len(cell.source))]

    @DocInherit
    def render_code(self, cell):
        if not cell.input:
            return []

        lines = ['In[%s]:' % cell.prompt_number, '']
        lines.extend(rst_directive('.. code:: python', cell.input))

        for output in cell.outputs:
            conv_fn = self.dispatch(output.output_type)
            lines.extend(conv_fn(output))

        return lines

    @DocInherit
    def render_markdown(self, cell):
        return [cell.source]

    @DocInherit
    def render_plaintext(self, cell):
        return [cell.source]

    @DocInherit
    def render_pyout(self, output):
        lines = ['Out[%s]:' % output.prompt_number, '']

        # output is a dictionary like object with type as a key
        if 'latex' in output:
            lines.extend(rst_directive('.. math::', output.latex))

        if 'text' in output:
            lines.extend(rst_directive('.. parsed-literal::', output.text))

        return lines

    @DocInherit
    def _img_lines(self, img_file):
        return ['.. image:: %s' % img_file, '']
    
    @DocInherit
    def render_stream(self, output):
        lines = []

        if 'text' in output:
            lines.extend(rst_directive('.. parsed-literal::', output.text))

        return lines

    @DocInherit
    def render_unknown(self, cell):
        return rst_directive('.. warning:: Unknown cell') + [repr(cell)]


class ConverterQuickHTML(Converter):
    extension = 'html'

    def optional_header(self):
        # XXX: inject the IPython standard CSS into here
        s = """<html>
        <head>
        </head>

        <body>
        """
        return s.splitlines()

    def optional_footer(self):
        s = """</body>
        </html>
        """
        return s.splitlines()

    @DocInherit
    def render_heading(self, cell):
        marker = cell.level
        return ['<h{1}>\n  {0}\n</h{1}>'.format(cell.source, marker)]

    @DocInherit
    def render_code(self, cell):
        if not cell.input:
            return []

        lines = ['<table>']
        lines.append('<tr><td><tt>In [<b>%s</b>]:</tt></td><td><tt>' % cell.prompt_number)
        lines.append("<br>\n".join(cell.input.splitlines()))
        lines.append('</tt></td></tr>')

        for output in cell.outputs:
            lines.append('<tr><td></td><td>')
            conv_fn = self.dispatch(output.output_type)
            lines.extend(conv_fn(output))
            lines.append('</td></tr>')
        
        lines.append('</table>')
        return lines

    @DocInherit
    def render_markdown(self, cell):
        return ["<pre>"+cell.source+"</pre>"]

    @DocInherit
    def render_plaintext(self, cell):
        return ["<pre>"+cell.source+"</pre>"]

    @DocInherit
    def render_pyout(self, output):
        lines = ['<tr><td><tt>Out[<b>%s</b>]:</tt></td></tr>' % output.prompt_number, '<td>']

        # output is a dictionary like object with type as a key
        if 'latex' in output:
            lines.append("<pre>")
            lines.extend(indent(output.latex))
            lines.append("</pre>")

        if 'text' in output:
            lines.append("<pre>")
            lines.extend(indent(output.text))
            lines.append("</pre>")

        return lines

    @DocInherit
    def _img_lines(self, img_file):
        return ['<img src="%s">' % img_file, '']

    @DocInherit
    def render_stream(self, output):
        lines = []

        if 'text' in output:
            lines.append(output.text)

        return lines


class ConverterLaTeX(Converter):
    """Converts a notebook to a .tex file suitable for pdflatex.

    Note: this converter *needs*:

    - `pandoc`: for all conversion of markdown cells.  If your notebook only
       has Raw cells, pandoc will not be needed.
    
    -  `inkscape`: if your notebook has SVG figures.  These need to be
       converted to PDF before inclusion in the TeX file, as LaTeX doesn't
       understand SVG natively.
    
    You will in general obtain much better final PDF results if you configure
    the matplotlib backend to create SVG output with 

    %config InlineBackend.figure_format = 'svg'

    (or set the equivalent flag at startup or in your configuration profile).
    """
    extension = 'tex'
    documentclass = 'article'
    documentclass_options = '11pt,english'
    heading_map = {1: r'\section',
                   2: r'\subsection',
                   3: r'\subsubsection',
                   4: r'\paragraph',
                   5: r'\subparagraph',
                   6: r'\subparagraph'}

    def env(self, environment, lines):
        """Return list of environment lines for input lines

        Parameters
        ----------
        env : string
          Name of the environment to bracket with begin/end.

        lines: """
        out = [r'\begin{%s}' % environment]
        if isinstance(lines, basestring):
            out.append(lines)
        else:  # list
            out.extend(lines)
        out.append(r'\end{%s}' % environment)
        return out

    def convert(self):
        # The main body is done by the logic in the parent class, and that's
        # all we need if preamble support has been turned off.
        body = super(ConverterLaTeX, self).convert()
        if not self.with_preamble:
            return body
        # But if preamble is on, then we need to construct a proper, standalone
        # tex file.
        
        # Tag the document at the top and set latex class
        final = [ r'%% This file was auto-generated by IPython, do NOT edit',
                  r'%% Conversion from the original notebook file:',
                  r'%% {0}'.format(self.infile),
                  r'%%',
                  r'\documentclass[%s]{%s}' % (self.documentclass_options,
                                               self.documentclass),
                  '',
                 ]
        # Load our own preamble, which is stored next to the main file.  We
        # need to be careful in case the script entry point is a symlink
        myfile = __file__ if not os.path.islink(__file__) else \
          os.readlink(__file__)
        with open(os.path.join(os.path.dirname(myfile), 'preamble.tex')) as f:
            final.append(f.read())
            
        # Load any additional user-supplied preamble
        if self.user_preamble:
            final.extend(['', '%% Adding user preamble from file:',
                          '%% {0}'.format(self.user_preamble), ''])
            with open(self.user_preamble) as f:
                final.append(f.read())
                
        # Include document body
        final.extend([ r'\begin{document}', '',
                       body,
                       r'\end{document}', ''])
        # Retun value must be a string
        return '\n'.join(final)
        
    @DocInherit
    def render_heading(self, cell):
        marker = self.heading_map[cell.level]
        return ['%s{%s}\n\n' % (marker, cell.source) ]

    @DocInherit
    def render_code(self, cell):
        if not cell.input:
            return []

        # Cell codes first carry input code, we use lstlisting for that
        lines = [r'\begin{codecell}']
        
        lines.extend(self.env('codeinput',
                              self.env('lstlisting', cell.input)))

        outlines = []
        for output in cell.outputs:
            conv_fn = self.dispatch(output.output_type)
            outlines.extend(conv_fn(output))

        # And then output of many possible types; use a frame for all of it.
        if outlines:
            lines.extend(self.env('codeoutput', outlines))

        lines.append(r'\end{codecell}')

        return lines


    @DocInherit
    def _img_lines(self, img_file):
        return self.env('center',
                [r'\includegraphics[width=3in]{%s}' % img_file, r'\par'])

    def _svg_lines(self, img_file):
        base_file = os.path.splitext(img_file)[0]
        pdf_file = base_file + '.pdf'
        subprocess.check_call(['inkscape', '--export-pdf=%s' % pdf_file,
                               img_file])
        return self._img_lines(pdf_file)

    @DocInherit
    def render_stream(self, output):
        lines = []

        if 'text' in output:
            lines.extend(self.env('verbatim', output.text.strip()))

        return lines

    @DocInherit
    def render_markdown(self, cell):
        return [markdown2latex(cell['source'])]
        
    @DocInherit
    def render_pyout(self, output):
        lines = []

        # output is a dictionary like object with type as a key
        if 'latex' in output:
            lines.extend(output.latex)

        if 'text' in output:
            lines.extend(self.env('verbatim', output.text))

        return lines

    @DocInherit
    def render_pyerr(self, output):
        # Note: a traceback is a *list* of frames.
        return self.env('traceback',
                        self.env('verbatim', 
                                 remove_ansi('\n'.join(output.traceback))))

    @DocInherit
    def render_unknown(self, cell):
        return self.env('verbatim', pprint.pformat(cell))


def rst2simplehtml(infile):
    """Convert a rst file to simplified html suitable for blogger.

    This just runs rst2html with certain parameters to produce really simple
    html and strips the document header, so the resulting file can be easily
    pasted into a blogger edit window.
    """

    # This is the template for the rst2html call that produces the cleanest,
    # simplest html I could find.  This should help in making it easier to
    # paste into the blogspot html window, though I'm still having problems
    # with linebreaks there...
    cmd_template = ("rst2html --link-stylesheet --no-xml-declaration "
                    "--no-generator --no-datestamp --no-source-link "
                    "--no-toc-backlinks --no-section-numbering "
                    "--strip-comments ")

    cmd = "%s %s" % (cmd_template, infile)
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    html, stderr = proc.communicate()
    if stderr:
        raise IOError(stderr)

    # Make an iterator so breaking out holds state.  Our implementation of
    # searching for the html body below is basically a trivial little state
    # machine, so we need this.
    walker = iter(html.splitlines())

    # Find start of main text, break out to then print until we find end /div.
    # This may only work if there's a real title defined so we get a 'div class'
    # tag, I haven't really tried.
    for line in walker:
        if line.startswith('<body>'):
            break

    newfname = os.path.splitext(infile)[0] + '.html'
    with open(newfname, 'w') as f:
        for line in walker:
            if line.startswith('</body>'):
                break
            f.write(line)
            f.write('\n')

    return newfname

known_formats = "rst (default), html, quick-html, latex"

def main(infile, format='rst'):
    """Convert a notebook to html in one step"""
    # XXX: this is just quick and dirty for now. When adding a new format,
    # make sure to add it to the `known_formats` string above, which gets
    # printed in in the catch-all else, as well as in the help
    if format == 'rst':
        converter = ConverterRST(infile)
        converter.render()
    elif format == 'html':
        #Currently, conversion to html is a 2 step process, nb->rst->html
        converter = ConverterRST(infile)
        rstfname = converter.render()
        rst2simplehtml(rstfname)
    elif format == 'quick-html':
        converter = ConverterQuickHTML(infile)
        rstfname = converter.render()
    elif format == 'latex':
        converter = ConverterLaTeX(infile)
        latexfname = converter.render()
    else:
        raise SystemExit("Unknown format '%s', " % format +
                "known formats are: " + known_formats)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawTextHelpFormatter)
    # TODO: consider passing file like object around, rather than filenames
    # would allow us to process stdin, or even http streams
    #parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)

    #Require a filename as a positional argument
    parser.add_argument('infile', nargs=1)
    parser.add_argument('-f', '--format', default='rst',
                        help='Output format. Supported formats: \n' +
                        known_formats)
    args = parser.parse_args()
    main(infile=args.infile[0], format=args.format)
