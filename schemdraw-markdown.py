################################################################################
"""
Schemdraw Markdown - A simpler way to document simple circuits in markdown.

License: MIT
"""
################################################################################

import re
from xml.etree import ElementTree as etree

import markdown


# For details see https://pythonhosted.org/Markdown/extensions/api.html#blockparser
class SchemDrawPreprocessor(markdown.preprocessors.Preprocessor):
    """Schemdraw Preprocessor for Markdown"""

    pass # TODO




# For details see https://pythonhosted.org/Markdown/extensions/api.html#extendmarkdown
class SchemDrawMarkdownExtension(markdown.Extension):
    # For details see https://pythonhosted.org/Markdown/extensions/api.html#configsettings
    def __init__(self, **kwargs):
        self.config = {
            'alt': ["schematic drawing", "Text to show when image is not available. Defaults to 'schematic drawing'"],
            'title': ["", "Tooltip for the diagram"],
            'priority': ["30", "Extension priority. Higher values means the extension is applied sooner than others. "
                               "Defaults to 30"],
        }

        # Fix to make links navigable in SVG diagrams
        etree.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

        super(SchemDrawMarkdownExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        blockprocessor = SchemDrawPreprocessor(md)
        blockprocessor.config = self.getConfigs()
        # need to go before both fenced_code_block and things like retext's PosMapMarkPreprocessor.
        # Need to go after mdx_include.
        if markdown.__version_info__[0] < 3:
            md.preprocessors.add('schemdraw', blockprocessor, '_begin')
        else:
            md.preprocessors.register(blockprocessor, 'schemdraw', int(blockprocessor.config['priority']))


def makeExtension(**kwargs):
    return SchemDrawMarkdownExtension(**kwargs)

# END
