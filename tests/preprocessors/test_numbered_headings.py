"""
Module with tests for the Numbered Headings preprocessor.
"""

from nbformat import v4 as nbformat

from nbconvert.preprocessors.numbered_headings import NumberedHeadingsPreprocessor

from .base import PreprocessorTestsBase

MARKDOWN_1 = """
# Heading 1

## Sub-heading

some content
"""

MARKDOWN_1_POST = """
# 1 Heading 1

## 1.1 Sub-heading

some content
"""


MARKDOWN_2 = """

## Second sub-heading

# Another main heading

## Sub-heading


some more content

### Third heading
"""

MARKDOWN_2_POST = """

## 1.2 Second sub-heading

# 2 Another main heading

## 2.1 Sub-heading


some more content

### 2.1.1 Third heading
"""


class TestNumberedHeadings(PreprocessorTestsBase):
    def build_notebook(self):
        cells = [
            nbformat.new_code_cell(source="$ e $", execution_count=1),
            nbformat.new_markdown_cell(source=MARKDOWN_1),
            nbformat.new_code_cell(source="$ e $", execution_count=1),
            nbformat.new_markdown_cell(source=MARKDOWN_2),
        ]

        return nbformat.new_notebook(cells=cells)

    def build_preprocessor(self):
        """Make an instance of a preprocessor"""
        preprocessor = NumberedHeadingsPreprocessor()
        preprocessor.enabled = True
        return preprocessor

    def test_constructor(self):
        """Can a ClearOutputPreprocessor be constructed?"""
        self.build_preprocessor()

    def test_output(self):
        """Test the output of the NumberedHeadingsPreprocessor"""
        nb = self.build_notebook()
        res = self.build_resources()
        preprocessor = self.build_preprocessor()
        nb, res = preprocessor(nb, res)
        print(nb.cells[1].source)
        assert nb.cells[1].source.strip() == MARKDOWN_1_POST.strip()
        assert nb.cells[3].source.strip() == MARKDOWN_2_POST.strip()
