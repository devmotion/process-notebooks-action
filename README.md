# Process notebooks action

This action exports Jupyter notebooks to HTML files and generates copies of
the notebooks with empty code cells.

Code cells with the tag `keep` are not emptied.

## Inputs

## `working_directory`

**Required** The working directory containing the notebooks to be exported.

## Example usage

```yml
uses: uu-sml/process-notebooks-action@v1
with:
  working_directory: exercises/python
```
