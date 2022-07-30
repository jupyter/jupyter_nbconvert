import os
import tempfile
import sys

from jupyter_core.paths import jupyter_path
from traitlets import default

from .html import HTMLExporter


class QtExporter(HTMLExporter):

    paginate = None

    def __init__(self, *args, **kwargs):
        self.format = self.output_mimetype.split("/")[-1]
        super().__init__(*args, **kwargs)

    @default("file_extension")
    def _file_extension_default(self):
        return "." + self.format

    @default("template_name")
    def _template_name_default(self):
        return "qt" + self.format

    @default("template_data_paths")
    def _template_data_paths_default(self):
        return jupyter_path("nbconvert", "templates", "qt" + self.format)

    def _check_launch_reqs(self):
        if sys.platform.startswith("win") and self.format == "png":
            raise RuntimeError("Exporting to PNG using Qt is currently not supported on Windows.")
        from .qt_screenshot import QT_INSTALLED

        if not QT_INSTALLED:
            raise RuntimeError(
                f"PyQtWebEngine is not installed to support Qt {self.format.upper()} conversion. "
                f"Please install `nbconvert[qt{self.format}]` to enable."
            )
        from .qt_screenshot import QtScreenshot

        return QtScreenshot

    def run_pyqtwebengine(self, html):
        """Run pyqtwebengine."""

        ext = ".html"
        temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        filename = f"{temp_file.name[:-len(ext)]}.{self.format}"
        with temp_file:
            temp_file.write(html.encode("utf-8"))

        try:
            QtScreenshot = self._check_launch_reqs()
            s = QtScreenshot()
            s.capture(f"file://{temp_file.name}", filename, self.paginate)
        finally:
            # Ensure the file is deleted even if pyqtwebengine raises an exception
            os.unlink(temp_file.name)
        return s.data

    def from_notebook_node(self, nb, resources=None, **kw):
        self._check_launch_reqs()
        html, resources = super().from_notebook_node(nb, resources=resources, **kw)

        self.log.info(f"Building {self.format.upper()}")
        data = self.run_pyqtwebengine(html)
        self.log.info(f"{self.format.upper()} successfully created")

        # convert output extension
        # the writer above required it to be html
        resources["output_extension"] = f".{self.format}"

        return data, resources
