
import sys
from pathlib import Path


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Kaxe'
copyright = '2024, Valter Yde Daugberg'
author = 'Valter Yde Daugberg'
release = '18-12-2023'

# patch path
sys.path.insert(0, str(Path('..', 'src').resolve()))

import kaxe


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# pip install --upgrade myst-parser

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    "myst_parser"
]


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
