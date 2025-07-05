# docs/conf.py
import os
import sys
sys.path.insert(0, os.path.abspath(".."))

project = "snmpwalk-parser"
author = "Kunal Raut"
release = "1.0.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",  # For Markdown (.md) support
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
