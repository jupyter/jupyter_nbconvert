"""Export to PDF via puppeteer"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import asyncio

from pyppeteer import launch
from pyppeteer.util import check_chromium
from traitlets import Bool
from .html import HTMLExporter

class WebPDFExporter(HTMLExporter):
    """Writer designed to write to PDF files.

    This inherits from :class:`HTMLExporter`. It creates the HTML using the
    template machinery, and then runs puppeteer (through pyppeteer) to create
    a pdf.
    """
    export_from_notebook="PDF via Puppeteer"

    allow_chromium_download = Bool(False,
        help="Whether to allow downloading chromium if no suitable version is found on the system."
    ).tag(config=True)

    def run_puppeteer(self, html):
        """Run puppeteer."""

        async def main():
            browser = await launch()
            page = await browser.newPage()
            await page.goto('data:text/html,'+html, waitUntil='networkidle0')
            pdf_data = await page.pdf()
            await browser.close()
            return pdf_data

        pdf_data = asyncio.get_event_loop().run_until_complete(main())
        return pdf_data

    def from_notebook_node(self, nb, resources=None, **kw):
        if not self.allow_chromium_download and not check_chromium():
            raise RuntimeError("No suitable chromium executable found on the system. "
                               "Please use '--allow-chromium-download' to allow downloading one.")

        html, resources = super().from_notebook_node(
            nb, resources=resources, **kw
        )

        self.log.info("Building PDF")
        pdf_data = self.run_puppeteer(html)
        self.log.info('PDF successfully created')

        # convert output extension to pdf
        # the writer above required it to be html
        resources['output_extension'] = '.pdf'

        return pdf_data, resources
