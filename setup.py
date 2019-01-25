#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

# the name of the package
name = 'nbconvert'

#-----------------------------------------------------------------------------
# Minimal Python version sanity check
#-----------------------------------------------------------------------------

import sys

v = sys.version_info
if v[:2] < (2,7) or (v[0] >= 3 and v[:2] < (3,4)):
    error = "ERROR: %s requires Python version 2.7 or 3.4 or above." % name
    print(error, file=sys.stderr)
    sys.exit(1)

PY3 = (sys.version_info[0] >= 3)

#-----------------------------------------------------------------------------
# get on with it
#-----------------------------------------------------------------------------

import os
import setuptools
import io
import platform

from setuptools.command.bdist_egg import bdist_egg

from glob import glob
from io import BytesIO
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen
from subprocess import check_call


from distutils.core import setup
from distutils.cmd import Command
from distutils.command.build import build
from distutils.command.build_py import build_py
from distutils.command.sdist import sdist

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
pkg_root = pjoin(here, name)

packages = []
for d, _, _ in os.walk(pjoin(here, name)):
    if os.path.exists(pjoin(d, '__init__.py')):
        packages.append(d[len(here)+1:].replace(os.path.sep, '.'))

package_data = {
    'nbconvert.filters' : ['marked.js'],
    'nbconvert.resources' : ['style.min.css', '*.js', '*.js.map', '*.eot', '*.svg', '*.woff2', '*.ttf', '*.woff'],
    'nbconvert' : [
        'tests/files/*.*',
        'tests/exporter_entrypoint/*.py',
        'tests/exporter_entrypoint/*/*.*',
        'exporters/tests/files/*.*',
        'preprocessors/tests/files/*.*',
    ],
}


notebook_css_version = '5.4.0'
css_url = "https://cdn.jupyter.org/notebook/%s/style/style.min.css" % notebook_css_version


class FetchCSS(Command):
    description = "Fetch Notebook CSS from Jupyter CDN"
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _download(self):
        try:
            return urlopen(css_url).read()
        except Exception as e:
            if 'ssl' in str(e).lower():
                try:
                    import pycurl
                except ImportError:
                    print("Failed, try again after installing PycURL with `pip install pycurl` to avoid outdated SSL.", file=sys.stderr)
                    raise e
                else:
                    print("Failed, trying again with PycURL to avoid outdated SSL.", file=sys.stderr)
                    return self._download_pycurl()
            raise e

    def _download_pycurl(self):
        """Download CSS with pycurl, in case of old SSL (e.g. Python < 2.7.9)."""
        import pycurl
        c = pycurl.Curl()
        c.setopt(c.URL, css_url)
        buf = BytesIO()
        c.setopt(c.WRITEDATA, buf)
        c.perform()
        return buf.getvalue()

    def run(self):
        dest = os.path.join('nbconvert', 'resources', 'style.min.css')
        if not os.path.exists('.git') and os.path.exists(dest):
            # not running from git, nothing to do
            return
        print("Downloading CSS: %s" % css_url)
        try:
            css = self._download()
        except Exception as e:
            msg = "Failed to download css from %s: %s" % (css_url, e)
            print(msg, file=sys.stderr)
            if os.path.exists(dest):
                print("Already have CSS: %s, moving on." % dest)
            else:
                raise OSError("Need Notebook CSS to proceed: %s" % dest)
            return

        with open(dest, 'wb') as f:
            f.write(css)
        print("Downloaded Notebook CSS to %s" % dest)

def update_package_data(distribution):
    """update package_data to catch changes during setup"""
    build_py = distribution.get_command_obj('build_py')
    # distribution.package_data = find_package_data()
    # re-init build_py options which load package_data
    build_py.finalize_options()


node_root = os.path.join(here, '.')
npm_path = os.pathsep.join([
    os.path.join(node_root, 'node_modules', '.bin'),
                os.environ.get('PATH', os.defpath),
])

class NPM(Command):
    description = 'install package.json dependencies using npm'

    user_options = []

    node_modules = os.path.join(node_root, 'node_modules')

    targets = [
        os.path.join(here, 'nbconvert', 'resources', 'snapshot.js'),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_npm_name(self):
        npmName = 'npm'
        if platform.system() == 'Windows':
            npmName = 'npm.cmd'
        return npmName

    def has_npm(self):
        npmName = self.get_npm_name()
        try:
            check_call([npmName, '--version'])
            return True
        except:
            return False

    def should_run_npm_install(self):
        package_json = os.path.join(node_root, 'package.json')
        node_modules_exists = os.path.exists(self.node_modules)
        return self.has_npm()

    def run(self):
        has_npm = self.has_npm()
        if not has_npm:
            raise OSError("`npm` unavailable.  If you're running this command using sudo, make sure `npm` is available to sudo")

        env = os.environ.copy()
        env['PATH'] = npm_path

        if self.should_run_npm_install():
            print("Installing build dependencies with npm.  This may take a while...")
            npmName = self.get_npm_name();
            check_call([npmName, 'install'], cwd=node_root, stdout=sys.stdout, stderr=sys.stderr)
            os.utime(self.node_modules, None)

        for t in self.targets:
            if not os.path.exists(t):
                msg = 'Missing file: %s' % t
                if not has_npm:
                    msg += '\nnpm is required to build a development version of widgetsnbextension'
                raise ValueError(msg)

        # update package data in case this created new files
        update_package_data(self.distribution)

cmdclass = {'css': FetchCSS, 'js': NPM}


class bdist_egg_disabled(bdist_egg):
    """Disabled version of bdist_egg

    Prevents setup.py install performing setuptools' default easy_install,
    which it should never ever do.
    """
    def run(self):
        sys.exit("Aborting implicit building of eggs. Use `pip install .` to install from source.")

def css_first(command):
    class CSSFirst(command):
        def run(self):
            self.distribution.run_command('css')
            return command.run(self)
    return CSSFirst

is_repo = os.path.exists(os.path.join(here, '.git'))

def js_first(command, strict=False):
    """decorator for building minified js/css prior to another command"""
    class JSFirst(command):
        def run(self):
            jsdeps = self.distribution.get_command_obj('js')
            if not is_repo and all(os.path.exists(t) for t in jsdeps.targets):
                # sdist, nothing to do
                command.run(self)
                return

            try:
                self.distribution.run_command('js')
            except Exception as e:
                missing = [t for t in jsdeps.targets if not os.path.exists(t)]
                if strict or missing:
                    print('rebuilding js and css failed')
                    if missing:
                        print('missing files: %s' % missing)
                    raise e
                else:
                    print('rebuilding js and css failed (not a problem)')
                    print(str(e))
            command.run(self)
            update_package_data(self.distribution)
    return JSFirst

cmdclass['build'] = js_first(css_first(build))
cmdclass['sdist'] = js_first(css_first(sdist), strict=True)
cmdclass['bdist_egg'] = bdist_egg if 'bdist_egg' in sys.argv else bdist_egg_disabled



for d, _, _ in os.walk(pjoin(pkg_root, 'templates')):
    g = pjoin(d[len(pkg_root)+1:], '*.*')
    package_data['nbconvert'].append(g)

version_ns = {}
with open(pjoin(here, name, '_version.py')) as f:
    exec(f.read(), {}, version_ns)

with io.open(pjoin(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

long_description="""

Nbconvert is a Command Line tool and Python library and API to process and
convert Jupyter notebook into a variety of other formats.

Using nbconvert enables:

  - presentation of information in familiar formats, such as PDF.
  - publishing of research using LaTeX and opens the door for embedding notebooks in papers.
  - collaboration with others who may not use the notebook in their work.
  - sharing contents with many people via the web using HTML.
"""

setup_args = dict(
    name            = name,
    description     = "Converting Jupyter Notebooks",
    long_description_content_type   = 'text/markdown',
    version         = version_ns['__version__'],
    scripts         = glob(pjoin('scripts', '*')),
    packages        = packages,
    long_description= long_description,
    package_data    = package_data,
    cmdclass        = cmdclass,
    python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    author          = 'Jupyter Development Team',
    author_email    = 'jupyter@googlegroups.com',
    url             = 'https://jupyter.org',
    project_urls={
        'Documentation': 'https://nbconvert.readthedocs.io/en/latest/',
        'Funding'      : 'https://numfocus.org/',
        'Source'       : 'https://github.com/jupyter/nbconvert',
        'Tracker'      : 'https://github.com/jupyter/nbconvert/issues',
    },
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Interactive', 'Interpreter', 'Shell', 'Web'],
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

setuptools_args = {}
install_requires = setuptools_args['install_requires'] = [
    'mistune>=0.8.1',
    'jinja2',
    'pygments',
    'traitlets>=4.2',
    'jupyter_core',
    'nbformat>=4.4',
    'entrypoints>=0.2.2',
    'bleach',
    'pandocfilters>=1.4.1',
    'testpath',
    'defusedxml',
]
jupyter_client_req = 'jupyter_client>=4.2'

extra_requirements = {
    'test': ['pytest', 'pytest-cov', 'ipykernel', jupyter_client_req, 'ipywidgets>=7', 'PyChromeDevTools', 'pillow'],
    'serve': ['tornado>=4.0'],
    'snapshot': ['PyChromeDevTools'],
    'execute': [jupyter_client_req],
    'docs': ['sphinx>=1.5.1',
             'sphinx_rtd_theme',
             'nbsphinx>=0.2.12',
             'sphinxcontrib_github_alt',
             'ipython',
             jupyter_client_req,
             ],
}

extra_requirements['all'] = sum(extra_requirements.values(), [])
setuptools_args['extras_require'] = extra_requirements

if 'setuptools' in sys.modules:
    from setuptools.command.develop import develop
    cmdclass['develop'] = css_first(develop)
    # force entrypoints with setuptools (needed for Windows, unconditional because of wheels)
    setup_args['entry_points'] = {
        'console_scripts': [
            'jupyter-nbconvert = nbconvert.nbconvertapp:main',
        ],
        "nbconvert.exporters" : [
            'custom=nbconvert.exporters:TemplateExporter',
            'html=nbconvert.exporters:HTMLExporter',
            'slides=nbconvert.exporters:SlidesExporter',
            'latex=nbconvert.exporters:LatexExporter',
            'pdf=nbconvert.exporters:PDFExporter',
            'markdown=nbconvert.exporters:MarkdownExporter',
            'python=nbconvert.exporters:PythonExporter',
            'rst=nbconvert.exporters:RSTExporter',
            'notebook=nbconvert.exporters:NotebookExporter',
            'asciidoc=nbconvert.exporters:ASCIIDocExporter',
            'script=nbconvert.exporters:ScriptExporter']
    }
    setup_args.pop('scripts', None)

    setup_args.update(setuptools_args)

if __name__ == '__main__':
    setup(**setup_args)
