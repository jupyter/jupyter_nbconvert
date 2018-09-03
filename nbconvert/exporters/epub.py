"""Export to Epub via latex"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from traitlets import  Instance
from ipython_genutils.tempdir import TemporaryWorkingDirectory
from .markdown import MarkdownExporter
from ..utils.pandoc import pandoc

class EpubExporter(MarkdownExporter):
    """Writer designed to write to Epub files.

    This inherits from :class:`MarkdownExporter`. It creates a markdown file in
    a temporary directory using the template machinery, and then runs pandoc
    to create a epub.
    """

    writer = Instance("nbconvert.writers.FilesWriter", args=())

    def from_notebook_node(self, nb, resources=None, **kw):
        markdown, resources = super(EpubExporter, self).from_notebook_node(
            nb, resources=resources, **kw
        )
        
        self._captured_outputs = []
        with TemporaryWorkingDirectory():
            notebook_name = 'notebook'
            md_file = self.writer.write(markdown, resources, notebook_name=notebook_name)
            with open(md_file) as fp:
                in_mem_md = fp.read()
            self.log.info("Building Epub")
            epub_file = notebook_name + '.epub'
            pandoc(in_mem_md,'markdown','epub',extra_args=['-o',epub_file]) 
            self.log.info("Epub successfully created")
            with open(epub_file, 'rb') as f:
                epub_data = f.read()
        
        # convert output extension to epub
        # the writer above required it to be markdown
        resources['output_extension'] = '.epub'
        # clear figure outputs, extracted by markdown export,
        # so we don't claim to be a multi-file export.
        resources.pop('outputs', None)
        
        return epub_data, resources
    
