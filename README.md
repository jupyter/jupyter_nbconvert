# nbconvert

### Jupyter Notebook Conversion

[![Build Status](https://github.com/jupyter/nbconvert/actions/workflows/tests.yml/badge.svg?query=branch%3Amain++)](https://github.com/jupyter/nbconvert/actions/workflows/tests.yml/badge.svg?query=branch%3Amain++)
[![Documentation Status](https://readthedocs.org/projects/nbconvert/badge/?version=latest)](https://nbconvert.readthedocs.io/en/latest/?badge=latest)

The **nbconvert** tool, `jupyter nbconvert`, converts notebooks to various other
formats via [Jinja] templates. The nbconvert tool allows you to convert an
`.ipynb` notebook file into various static formats including:

- HTML
- LaTeX
- PDF
- Reveal JS
- Markdown (md)
- ReStructured Text (rst)
- executable script

## Usage

From the command line, use nbconvert to convert a Jupyter notebook (_input_) to a
a different format (_output_). The basic command structure is:

```
$ jupyter nbconvert --to <output format> <input notebook>
```

where `<output format>` is the desired output format and `<input notebook>` is the
filename of the Jupyter notebook.

### Example: Convert a notebook to HTML

Convert Jupyter notebook file, `mynotebook.ipynb`, to HTML using:

```
$ jupyter nbconvert --to html mynotebook.ipynb
```

This command creates an HTML output file named `mynotebook.html`.

## Dev Install

Check if pandoc is installed (`pandoc --version`); if needed, install:

```
sudo apt-get install pandoc
```

Or

```
brew install pandoc
```

Install nbconvert for development using:

```
git clone https://github.com/jupyter/nbconvert.git
cd nbconvert
pip install -e .
```

Running the tests after a dev install above:

```
pip install nbconvert[test]
py.test --pyargs nbconvert
```

## Documentation

- [Documentation for Jupyter nbconvert](https://nbconvert.readthedocs.io/en/latest/)
- [nbconvert examples on GitHub](https://github.com/jupyter/nbconvert-examples)
- [Documentation for Project Jupyter](https://jupyter.readthedocs.io/en/latest/index.html)

## Technical Support

- [Issues and Bug Reports](https://github.com/jupyter/nbconvert/issues): A place to report
  bugs or regressions found for nbconvert
- [Community Technical Support and Discussion - Discourse](https://discourse.jupyter.org/): A place for
  installation, configuration, and troubleshooting assistannce by the Jupyter community.
  As a non-profit project and maintainers who are primarily volunteers, we encourage you
  to ask questions and share your knowledge on Discourse.

## Jupyter Resources

- [Jupyter mailing list](https://groups.google.com/forum/#!forum/jupyter)
- [Project Jupyter website](https://jupyter.org)

## About the Jupyter Development Team

The Jupyter Development Team is the set of all contributors to the Jupyter project.
This includes all of the Jupyter subprojects.

The core team that coordinates development on GitHub can be found here:
https://github.com/jupyter/.

## Our Copyright Policy

Jupyter uses a shared copyright model. Each contributor maintains copyright
over their contributions to Jupyter. But, it is important to note that these
contributions are typically only changes to the repositories. Thus, the Jupyter
source code, in its entirety is not the copyright of any single person or
institution. Instead, it is the collective copyright of the entire Jupyter
Development Team. If individual contributors want to maintain a record of what
changes/contributions they have specific copyright on, they should indicate
their copyright in the commit message of the change, when they commit the
change to one of the Jupyter repositories.

With this in mind, the following banner should be used in any source code file
to indicate the copyright and license terms:

```
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
```

[jinja]: http://jinja.pocoo.org/
