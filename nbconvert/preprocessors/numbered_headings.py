"""
Preprocessor that transforms markdown cells: Insert numbering in from of heading
"""

import re

from nbconvert.preprocessors.base import Preprocessor


class NumberedHeadingsPreprocessor(Preprocessor):
    """Pre-processor that will rewrite markdown headings to include numberings."""

    def __init__(self, *args, **kwargs):
        """Init"""
        super().__init__(*args, **kwargs)
        self.current_numbering = [0]

    def format_numbering(self):
        """Return a string representation of the current numbering"""
        return ".".join(str(n) for n in self.current_numbering)

    def _inc_current_numbering(self, level):
        """Increase internal counter keeping track of numberings"""
        if level > len(self.current_numbering):
            self.current_numbering = self.current_numbering + [0] * (
                level - len(self.current_numbering)
            )
        elif level < len(self.current_numbering):
            self.current_numbering = self.current_numbering[:level]
        self.current_numbering[level - 1] += 1

    def _transform_markdown_line(self, line, resources):
        """Rewrites one markdown line, if needed"""
        if m := re.match(r"^(?P<level>#+) (?P<heading>.*)", line):
            level = len(m.group("level"))
            self._inc_current_numbering(level)
            old_heading = m.group("heading").strip()
            new_heading = self.format_numbering() + " " + old_heading
            return "#" * level + " " + new_heading

        return line

    def preprocess_cell(self, cell, resources, index):
        """Rewrites all the headings in the cell if it is markdown"""
        if cell["cell_type"] == "markdown":
            cell["source"] = "\n".join(
                self._transform_markdown_line(line, resources)
                for line in cell["source"].splitlines()
            )

        return cell, resources
