# Process notebooks action

This action exports Jupyter notebooks to HTML files and generates copies of
the notebooks with empty code cells.

More concretely, the action
- removes cells with the tag 'remove' (regardless of the cell type),
- keeps the content of code cells with the tag `keep`,
- keeps the content of code cells without the tag 'keep' that is enclosed by `#<keep>\n` and `#</keep>\n`.

A code cell may contain multiple `#<keep>/n`-`#</keep>/n` blocks. At the end of a cell thw newline character may be omitted, i.e. a cell may end with `#</keep>`.

## Inputs

## `working_directory`

**Required** The working directory containing the notebooks to be exported.

## Example usage

```yml
uses: uu-sml/process-notebooks-action@v1
with:
  working_directory: exercises/python
```
