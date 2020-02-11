#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export jupyter notebooks to html and a separate
notebook without code striped.

To prevent a code cell from being emptied, add the tag 
`keep` to the cell. Click View -> Cell Toolbar -> Tags.


To run from utils directory and export to ../build
python generate_public.py -o .. ..

Or to run from python directory
python utils/generate_public.py .

Export a single file
python utils/generate_public.py session_2.py

By: Johan Wågberg 2019
"""
import json
import argparse
import nbformat
import re
from traitlets.config import Config
from nbconvert import HTMLExporter, PDFExporter, LatexExporter
from nbconvert.writers import FilesWriter
from bs4 import BeautifulSoup
from pathlib import Path
from itertools import tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def export_html(file, path):
    
    with file.open() as f:
        notebook = nbformat.read(f, as_version=4)
        
        c = Config()
        c.FilesWriter.build_directory = path.parent.as_posix()
           
        for cell in notebook.cells:
            if cell.get('cell_type') == 'code':
                cell.source = re.sub('#<\/?keep>\n', '', cell.source)
        
        html_exporter = HTMLExporter(config=c)
        html = html_exporter.from_notebook_node(notebook)
        
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

def parse_cell(string):
    s = re.finditer('#<keep>\n', string)
    e = re.finditer('#</keep>\n', string)
    new = []
    while True:
        try:
            new.append(string[next(s).end():next(e).start()])
        except StopIteration:
            break
    return "".join(new)

def parse_code_cell(cell):
    if cell.execution_count:
        cell.execution_count = None
    if cell.outputs:
        cell.outputs = []
    if not ('keep' in cell.get('metadata', {}).get('tags', [])):
        cell.source = parse_cell(cell.source)


def export_without_code(file, path):
    with file.open() as f:
        notebook = nbformat.read(f, as_version=4)
        new_cells = []
        last_was_empty_code_cell = False
        for cell in notebook.cells:    
            if cell.cell_type == 'code':
                parse_code_cell(cell)
                if not cell.source: # is empty
                    if not last_was_empty_code_cell:
                        new_cells.append(cell)
                    last_was_empty_code_cell = True
                else: # not empty
                    new_cells.append(cell)
                    last_was_empty_code_cell = False
            else:
                new_cells.append(cell)
                last_was_empty_code_cell = False
            cell['metadata']['tags'] = []
                
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
#                        required=True,
                        help="Path of a file or a folder of files")
    parser.add_argument("-e", "--extension",
                        default='ipynb',
                        help="File extension to filter by.")
    
    parser.add_argument("-o", "--outdir",
                        default=".",
                        help="Output directory.")
    
#    parser.add_argument("-r", "--recursive",
#                        action="store_true",
#                        default=False,
#                        help="Search recursively in subfolders.")
    
    return parser
   
def main():
    args = get_parser().parse_args()
    
    paths = [Path(path) for path in args.path]
    
    files = set()
    for path in paths:
        if path.is_file():
            if path.suffix == f".{args.extension}":
                files.add(path)
        else:
            files |= set(path.glob(f"./*.{args.extension}"))
#            if (args.recursive):
#                paths += path.glob("*")
    outdir = Path(args.outdir).resolve() / "build"
    for file in files:
        print(f"Processing {file.name}")
            
        html_file = outdir / "solutions" / f"{file.stem}.html"
        export_html(file, html_file)
        
        no_code_file = outdir / f"{file.stem}.{args.extension}"
        export_without_code(file, no_code_file)
    
if __name__ == "__main__":
    main()
    
