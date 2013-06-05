"""
Exporter that exports Basic HTML.
"""

#-----------------------------------------------------------------------------
# Copyright (c) 2013, the IPython Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from IPython.utils.traitlets import Unicode
from IPython.config import Config
from copy import deepcopy

import nbconvert.transformers.csshtmlheader

# local import
import exporter

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

class BasicHtmlExporter(exporter.Exporter):
    """
    Exports a basic HTML document.  This exporter assists with the export of
    HTML.  Inherit from it if you are writing your own HTML template and need
    custom transformers/filters.  If you don't need custom transformers/
    filters, just change the 'template_file' config option.  
    """
    
    file_extension = Unicode(
        'html', config=True, 
        help="Extension of the file that should be written to disk"
        )

    template_file = Unicode(
            'basichtml', config=True,
            help="Name of the template file to use")


    def __init__(self, transformers=None, filters=None, config=None, **kw):
       
        c = self.default_config
        if config :
            c.merge(config)
        
        super(BasicHtmlExporter, self).__init__(transformers=transformers,
                                                filters=filters,
                                                config=c,
                                                **kw)
        

    def _register_transformers(self):
        """
        Register all of the transformers needed for this exporter.
        """
        
        #Register the transformers of the base class.
        super(BasicHtmlExporter, self)._register_transformers()
        
        #Register CSSHtmlHeaderTransformer transformer
        self.register_transformer(nbconvert.transformers.csshtmlheader.CSSHtmlHeaderTransformer)
                    
