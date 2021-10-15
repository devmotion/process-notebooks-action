#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export Jupyter notebook(s) to HTML and a cleaned notebook.

In the cleaned notebook,
- cells tagged with 'remove' are removed (regardless of their type),
- code cells tagged with 'keep' are copied,
- and content of code cells without the tag 'keep' that is
  enclosed by '#<keep>\n' and '#</keep>\n' is kept.

A code cell may contain multiple '#<keep>/n'-'#</keep>/n' blocks.
At the end of a cell the newline character may be omitted, i.e. a
cell may end with '#</keep>'.

By: Johan Wågberg 2019
Modified by: David Widmann 2021
"""
import json
import argparse
import nbformat

import copy
import re

from traitlets.config import Config
from nbconvert import HTMLExporter, PDFExporter, LatexExporter
from nbconvert.writers import FilesWriter
from bs4 import BeautifulSoup
from pathlib import Path


def export_html(notebook, path):
    """Export `notebook` as HTML file to `path`."""
    c = Config()
    c.FilesWriter.build_directory = path.parent.as_posix()

    # remove '#<keep>' and '#</keep>'
    notebook = copy.deepcopy(notebook)
    for cell in notebook.cells:
        if cell.get('cell_type') == 'code':
            cell.source = re.sub('#<\/?keep>(?:\n|$)', '', cell.source)

    # export notebook as HTML
    html_exporter = HTMLExporter(config=c)
    html = html_exporter.from_notebook_node(notebook)

    # add CSS that makes it more difficult to copy solutions
    soup = BeautifulSoup(html[0], 'html5lib')    
    style = soup.new_tag('style')
    style.attrs['type'] = 'text/css'
    style.string = """.input .inner_cell .input_area pre {
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        -khtml-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }"""
    soup.head.append(style)

    writer = FilesWriter(config=c)
    writer.write(str(soup), *html[1:], path.stem)
    print(f"Writing file { path }")


def export_clean(notebook, path):
    """Clean `notebook` and save it as `path`."""
    new_cells = []
    last_was_empty_code_cell = False
    keep_regex = r'#<keep>\n(.*?)#</keep>(?:\n|$)'
    notebook = copy.deepcopy(notebook)
    for cell in notebook.cells:
        # obtain and remove tags
        tags = cell.get('metadata', {}).get('tags', [])
        cell['metadata']['tags'] = []

        # remove cells tagged with 'remove'
        if 'remove' in tags:
            continue

        # copy other non-code cells
        if cell.cell_type != 'code':
            new_cells.append(cell)
            last_was_empty_code_cell = False
            continue

        # handle remaining code cells
        # remove execution count (the number on the left side) and output
        if cell.execution_count:
            cell.execution_count = None
        if cell.outputs:
            cell.outputs = []

        if 'keep' in tags:
            # copy code cell if it is tagged with 'keep'
            new_cells.append(cell)
            last_was_empty_code_cell = not cell.source
        else:
            # otherwise only keep content between '#<keep>\n' and '#</keep>\n'
            # or '#</keep>$' (end of string)
            cell.source = "".join(re.findall(keep_regex, cell.source, re.DOTALL))

            # remove code cell completely if it is empty and the last cell was
            # also an empty code cell
            cell_is_empty = not cell.source
            if not (cell_is_empty and last_was_empty_code_cell):
                new_cells.append(cell)
                last_was_empty_code_cell = cell_is_empty

    notebook.cells = new_cells        
    with path.open('w') as file:
        json.dump(notebook, file)
        print(f"Writing file {path}")


def get_parser():
    """Get parser object for generate_public.py"""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("path",
                        nargs='+',
                        help="Path of a file or a folder of files")
    parser.add_argument("-e", "--extension",
                        default='ipynb',
                        help="File extension to filter by.")
    parser.add_argument("-o", "--outdir",
                        default=".",
                        help="Output directory (files are exported to subdirectory 'build').")
    return parser


def main():
    # parse arguments
    args = get_parser().parse_args()

    # find notebooks
    paths = [Path(path) for path in args.path]
    files = set()
    for path in paths:
        if path.is_file():
            if path.suffix == f".{args.extension}":
                files.add(path)
        else:
            files |= set(path.glob(f"./*.{args.extension}"))

    # define directory for exported files
    outdir = Path(args.outdir).resolve() / "build"

    for file in files:
        print(f"Processing {file.name}")

        # read notebook
        with file.open() as f:
            notebook = nbformat.read(f, as_version=4)

        # export as HTML
        html_file = outdir / "solutions" / f"{file.stem}.html"
        export_html(notebook, html_file)

        # export clean notebook
        clean_file = outdir / f"{file.stem}.{args.extension}"
        export_clean(notebook, clean_file)


if __name__ == "__main__":
    main()
