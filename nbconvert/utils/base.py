"""Global configuration class."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from traitlets import List
from traitlets.config.configurable import LoggingConfigurable
from traitlets import Unicode

class NbConvertBase(LoggingConfigurable):
    """Global configurable class for shared config

    Useful for display data priority that might be use by many transformers
    """

    display_data_priority = List(['text/html', 'application/pdf', 'text/latex', 'image/svg+xml', 'image/png', 'image/jpeg', 'text/plain'],
            
              help= """
                    An ordered list of preferred output type, the first
                    encountered will usually be used when converting discarding
                    the others.
                    """
            ).tag(config=True)

    default_language = Unicode('ipython', 
       help='DEPRECATED default highlight language, please use language_info metadata instead').tag(config=True)

    def __init__(self, **kw):
        super(NbConvertBase, self).__init__(**kw)
