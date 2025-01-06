"""Tests for HTMLExporter"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import re

from nbformat import v4
from traitlets.config import Config

from nbconvert.exporters.html import HTMLExporter

from .base import ExportersTestsBase


class TestHTMLExporter(ExportersTestsBase):
    """Tests for HTMLExporter"""

    exporter_class = HTMLExporter  # type:ignore
    should_include_raw = ["html"]  # type:ignore

    def test_constructor(self):
        """
        Can a HTMLExporter be constructed?
        """
        HTMLExporter()

    def test_export(self):
        """
        Can a HTMLExporter export something?
        """
        (output, resources) = HTMLExporter().from_filename(self._get_notebook())
        assert len(output) > 0

    def test_export_classic(self):
        """
        Can a HTMLExporter export using the 'classic' template?
        """
        (output, resources) = HTMLExporter(template_name="classic").from_filename(
            self._get_notebook()
        )
        assert len(output) > 0

    def test_export_notebook(self):
        """
        Can a HTMLExporter export using the 'lab' template?
        """
        (output, resources) = HTMLExporter(template_name="lab").from_filename(self._get_notebook())
        assert len(output) > 0

    def test_prompt_number(self):
        """
        Does HTMLExporter properly format input and output prompts?
        """
        no_prompt_conf = Config(
            {
                "TemplateExporter": {
                    "exclude_input_prompt": True,
                    "exclude_output_prompt": True,
                }
            }
        )
        exporter = HTMLExporter(config=no_prompt_conf, template_name="lab")
        (output, resources) = exporter.from_filename(
            self._get_notebook(nb_name="prompt_numbers.ipynb")
        )
        in_regex = r"In&nbsp;\[(.*)\]:"
        out_regex = r"Out\[(.*)\]:"

        assert not re.findall(in_regex, output)
        assert not re.findall(out_regex, output)

    def test_png_metadata(self):
        """
        Does HTMLExporter with the 'classic' template treat pngs with width/height metadata correctly?
        """
        exporter = HTMLExporter(template_name="classic")
        with self.assertLogs(exporter.log, level="WARN") as log:
            (output, resources) = exporter.from_filename(
                self._get_notebook(nb_name="pngmetadata.ipynb")
            )
            assert len(log.output) == 1
            assert "Alternative text is missing on 1 image(s)." in log.output[0]

        check_for_png = re.compile(
            r'<img alt="No description has been provided for this image"([^>]*?)>'
        )
        result = check_for_png.search(output)
        assert result
        attr_string = result.group(1)
        assert "width=" in attr_string
        assert "height=" in attr_string

    def test_javascript_output(self):
        nb = v4.new_notebook(
            cells=[
                v4.new_code_cell(
                    outputs=[
                        v4.new_output(
                            output_type="display_data",
                            data={"application/javascript": "javascript_output();"},
                        )
                    ]
                )
            ]
        )
        (output, resources) = HTMLExporter(template_name="classic").from_notebook_node(nb)
        self.assertIn("javascript_output", output)

    def test_mermaid_output(self):
        nb = v4.new_notebook(
            cells=[
                v4.new_code_cell(
                    outputs=[
                        v4.new_output(
                            output_type="display_data",
                            data={"text/vnd.mermaid": "flowchart LR\na --> b"},
                        )
                    ]
                )
            ]
        )
        (output, resources) = HTMLExporter(template_name="lab").from_notebook_node(nb)
        self.assertIn("""<div class="jp-Mermaid">""", output)
        self.assertIn("""<pre class="mermaid">""", output)

    def test_mermaid_prerendered_output(self):
        nb = v4.new_notebook(
            cells=[
                v4.new_code_cell(
                    outputs=[
                        v4.new_output(
                            output_type="display_data",
                            data={
                                "image/svg+xml": "<svg></svg>",
                                "text/vnd.mermaid": "flowchart LR\na --> b",
                            },
                        )
                    ]
                )
            ]
        )
        (output, resources) = HTMLExporter(template_name="lab").from_notebook_node(nb)
        self.assertNotIn("""<div class="jp-Mermaid">""", output)

    def test_attachments(self):
        (output, resources) = HTMLExporter(template_name="classic").from_file(
            self._get_notebook(nb_name="attachment.ipynb")
        )
        check_for_png = re.compile(r'<img alt="image.png" src="([^"]*?)"/>')
        result = check_for_png.search(output)
        assert result
        self.assertTrue(result.group(1).strip().startswith("data:image/png;base64,iVBOR"))

        check_for_data = re.compile(r'<img alt="image.png" src="(?P<url>[^"]*?)"')
        results = check_for_data.findall(output)
        assert results[0] != results[1], "attachments only need to be unique within a cell"
        assert "image/svg" in results[1], "second image should use svg"

    def test_custom_filter_highlight_code(self):
        # Overwriting filters takes place at: Exporter.from_notebook_node
        nb = v4.new_notebook()
        nb.cells.append(v4.new_code_cell("some_text"))

        def custom_highlight_code(source, language="python", metadata=None):
            return source + " ADDED_TEXT"

        filters = {"highlight_code": custom_highlight_code}
        (output, resources) = HTMLExporter(
            template_name="classic", filters=filters
        ).from_notebook_node(nb)
        self.assertTrue("ADDED_TEXT" in output)

    def test_basic_name(self):
        """
        Can a HTMLExporter export using the 'basic' template?
        """
        (output, resources) = HTMLExporter(template_name="basic").from_filename(
            self._get_notebook()
        )
        assert len(output) > 0

    def test_javascript_injection(self):
        for template in ["lab", "classic", "reveal"]:
            (output, resources) = HTMLExporter(template_name=template).from_filename(
                self._get_notebook("notebook_inject.ipynb")
            )

            # Check injection in the metadata.title of the Notebook
            assert "<script>alert('title')</script>" not in output

            # Check injection in the metadata.widgets of the Notebook
            assert "</script><script>alert('widgets')" not in output

            # Check injection in the cell.metadata.tags of the Notebook
            assert "<script>alert('cell_tag')</script>" not in output

            # Check injection in the cell.source of the Notebook
            assert "<script>alert('raw cell')</script>" not in output

            # Check injection in svg output
            assert "<script>alert('image/svg+xml output')</script>" not in output
            assert "<script>alert('svg_filename')</script>" not in output

            # Check injection in image filenames
            assert "<script>alert('png filenames')</script>" not in output
            assert "<script>alert('jpg filenames')</script>" not in output

            # Check injection in image data
            assert "<script>alert('image/png output')</script>" not in output
            assert "<script>alert('image/jpeg output')</script>" not in output

            # Check injection in image width/height
            assert "<script>alert('output.metadata.width png injection')</script>" not in output
            assert "<script>alert('output.metadata.height png injection')</script>" not in output

            # Check injection in widget view
            assert (
                "<script>alert('output.data.application/vnd.jupyter.widget-view+json injection')"
                not in output
            )

        # By design, text/html, text/markdown, application/javascript and markdown cells should allow
        # for JavaScript code execution
        for template in ["lab", "classic", "reveal"]:
            (output, resources) = HTMLExporter(template_name=template).from_filename(
                self._get_notebook("notebook_inject.ipynb")
            )

            assert "<script>alert('markdown cell')</script>" in output
            assert "<script>alert('text/markdown output')</script>" in output
            assert "<script>alert('text/html output')</script>" in output
            assert "alert('application/javascript output')" in output

        # But it's an opt-out
        for template in ["lab", "classic", "reveal"]:
            (output, resources) = HTMLExporter(
                template_name=template, sanitize_html=True
            ).from_filename(self._get_notebook("notebook_inject.ipynb"))

            assert "<script>alert('markdown cell')</script>" not in output
            assert "<script>alert('text/markdown output')</script>" not in output
            assert "<script>alert('text/html output')</script>" not in output
            assert "alert('application/javascript output')" not in output

    def test_language_code_not_set(self):
        (output, resources) = HTMLExporter(template_name="classic").from_filename(
            self._get_notebook()
        )
        assert '<html lang="en">' in output

    def test_set_language_code(self):
        exporter = HTMLExporter(template_name="classic", language_code="fr")
        (output, resources) = exporter.from_filename(self._get_notebook())
        assert '<html lang="fr">' in output

    def test_language_code_error(self):
        with self.assertLogs(level="WARN") as log:
            exporter = HTMLExporter(template_name="classic", language_code="zz")
            assert len(log.output) == 1
            assert '"zz" is not an ISO 639-1 language code.' in log.output[0]
        (output, resources) = exporter.from_filename(self._get_notebook())

        assert '<html lang="en">' in output


def test_syntax_highlight_leading_whitespace():
    """Test that syntax highlight doesn't strip leading spaces."""
    nb = v4.reads(r"""
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "29da71a9-ae40-4098-8c3b-31a98e79fc12",
   "metadata": {},
   "source": [
    "```APL\n",
    "      1+2×⍳3\n",
    "3 5 7\n",
    "```\n",
    "\n",
    "```\n",
    "      1+2×⍳3\n",
    "3 5 7\n",
    "```"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 5
}
    """)
    output, _ = HTMLExporter().from_notebook_node(nb)
    # Check that the second code block has the leading spaces
    assert "<pre><code>      1+2×⍳3\n3 5 7\n</code></pre>" in output

    # Check that the APL-formatted code block has the leading spaces
    assert '<span class="w">      </span>' in output
