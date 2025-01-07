"""Tests for the latex preprocessor"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import builtins
from unittest.mock import patch

import pytest

from nbconvert.exporters.exporter import Exporter
from nbconvert.exporters.webpdf import PLAYWRIGHT_INSTALLED, WebPDFExporter

from .base import ExportersTestsBase

real_import = builtins.__import__


class FakeBrowser:
    executable_path: str = ""


def monkey_import_notfound(name, globals_ctx=None, locals_ctx=None, fromlist=(), level=0):
    if name == "playwright.async_api":
        msg = "Fake missing"
        raise ModuleNotFoundError(msg)
    return real_import(name, globals=globals_ctx, locals=locals_ctx, fromlist=fromlist, level=level)


@pytest.mark.skipif(not PLAYWRIGHT_INSTALLED, reason="Playwright not installed")
class TestWebPDFExporter(ExportersTestsBase):
    """Contains test functions for webpdf.py"""

    exporter_class = WebPDFExporter  # type:ignore

    @pytest.mark.network
    def test_export(self):
        """
        Can a TemplateExporter export something?
        """
        (output, resources) = WebPDFExporter(allow_chromium_download=True).from_filename(
            self._get_notebook()
        )
        assert len(output) > 0

    @patch("playwright.async_api._generated.Playwright.chromium", return_value=FakeBrowser())
    def test_webpdf_without_chromium(self, mock_chromium):
        """
        Generate PDFs if chromium not present?
        """
        with pytest.raises(RuntimeError):
            WebPDFExporter(allow_chromium_download=False).from_filename(self._get_notebook())

    @patch("builtins.__import__", monkey_import_notfound)
    def test_webpdf_without_playwright(self):
        """
        Generate PDFs if playwright not installed?
        """
        with pytest.raises(RuntimeError):  # noqa
            base_exporter = Exporter()
            exporter = WebPDFExporter()
            with open(self._get_notebook(), encoding="utf-8") as f:
                nb = base_exporter.from_file(f, resources={})[0]
                # Have to do this as the very last action as traitlets do dynamic importing often
                exporter.from_notebook_node(nb)
