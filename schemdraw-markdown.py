################################################################################
"""
Schemdraw Markdown - A simpler way to document simple circuits in markdown.

License: MIT

This plugin implements a block extension which can be used to specify a
Schematic Diagram which will be converted into an image and inserted in the
document using [schemdraw](https://bitbucket.org/cdelker/schemdraw/src/master/).

Syntax:

    ::schemdraw:: [alt="text for alt"]
        schemdraw script diagram
    ::end-schemdraw::

Example:

    ::schemdraw:: alt="My super diagram"
        += elm.Resistor().right().label('1Ω')
        += elm.Capacitor().down().label('10μF')
        += elm.Line().left()
        += elm.SourceSin().up().label('10V')
    ::end-schemdraw::
"""
################################################################################

import re
import base64
import logging
from xml.etree import ElementTree as etree

import markdown


# use markdown_py with -v to enable warnings, or with --noisy to enable debug logs
logger = logging.getLogger('MARKDOWN')


# For details see https://pythonhosted.org/Markdown/extensions/api.html#blockparser
class SchemDrawPreprocessor(markdown.preprocessors.Preprocessor):
    # Regular expression inspired from fenced_code
    BLOCK_RE = re.compile(r'''
        (?P<indent>[ ]*)
        ::schemdraw:: 
        # args
        \s*(alt=(?P<quot2>"|')(?P<alt>.*?)(?P=quot2))?
        \s*(title=(?P<quot3>"|')(?P<title>.*?)(?P=quot3))?
        \s*(width=(?P<quot4>"|')(?P<width>[\w\s"']+%?)(?P=quot4))?
        \s*(height=(?P<quot5>"|')(?P<height>[\w\s"']+%?)(?P=quot5))?
        \s*(source=(?P<quot6>"|')(?P<source>.*?)(?P=quot6))?
        \s*\n
        (?P<code>.*?)(?<=\n)
        (?P=indent)::end-schemdraw::[ ]*$
        ''', re.MULTILINE | re.DOTALL | re.VERBOSE)

    FENCED_BLOCK_RE = re.compile(r'''
        (?P<indent>[ ]*)
        (?P<fence>(?:~{3}|`{3}))[ ]*            # Opening ``` or ~~~
        (\{?\.?schemdraw)[ ]*                   # Optional {, and lang
        # args
        \s*(alt=(?P<quot2>"|')(?P<alt>.*?)(?P=quot2))?
        \s*(title=(?P<quot3>"|')(?P<title>.*?)(?P=quot3))?
        \s*(width=(?P<quot4>"|')(?P<width>[\w\s"']+%?)(?P=quot4))?
        \s*(height=(?P<quot5>"|')(?P<height>[\w\s"']+%?)(?P=quot5))?
        \s*(source=(?P<quot6>"|')(?P<source>.*?)(?P=quot6))?
        [ ]*
        }?[ ]*\n                                # Optional closing }
        (?P<code>.*?)(?<=\n)
        (?P=indent)(?P=fence)[ ]*$
        ''', re.MULTILINE | re.DOTALL | re.VERBOSE)
    # (?P<indent>[ ]*)(?P<fence>(?:~{3}|`{3}))[ ]*(\{?\.?schemdraw)[ ]*\n(?P<code>.*?)(?<=\n)(?P=indent)(?P=fence)$
    FENCED_CODE_RE = re.compile(r'(?P<fence>(?:~{4,}|`{4,})).*?(?P=fence)',
                                re.MULTILINE | re.DOTALL | re.VERBOSE)
    """Schemdraw Preprocessor for Markdown"""

    def __init__(self, md):
        super(SchemDrawPreprocessor, self).__init__(md)

    def run(self, lines):
        text = '\n'.join(lines)
        idx = 0

        # loop until all text is parsed
        while idx < len(text):
            text1, idx1 = self._replace_block(text[idx:])
            text = text[:idx]+text1
            idx += idx1

        return text.split('\n')

    def _replace_block(self, text):
        # skip fenced code enclosing diagram
        m = self.FENCED_CODE_RE.search(text)
        if m:
            # check if before the fenced code there is a plantuml diagram
            m1 = self.FENCED_BLOCK_RE.search(text[:m.start()])
            if m1 is None:
                # no diagram, skip this block of text
                return text, m.end()+1

        # Parse configuration params
        m = self.FENCED_BLOCK_RE.search(text)
        if not m:
            m = self.BLOCK_RE.search(text)
            if not m:
                return text, len(text)

        # Parse configuration params
        alt = m.group('alt') if m.group('alt') else self.config['alt']
        title = m.group('title') if m.group('title') else self.config['title']
        width = m.group('width') if m.group('width') else None
        height = m.group('height') if m.group('height') else None
        source = m.group('source') if m.group('source') else None

        # Extract the PlantUML code.
        code = ""
        # Add extracted markdown diagram text.
        code += m.group('code')

        # Extract diagram source end convert it (if not external)
        diagram = self._render_diagram(code)
        self_closed = True  # tags are always self closing
        map_tag = ''

        # Firefox handles only base64 encoded SVGs
        data = 'data:image/svg+xml;base64,{0}'.format(
            base64.b64encode(diagram).decode('ascii')
        )
        img = etree.Element('img')
        img.attrib['src'] = data

        styles = []
        if 'style' in img.attrib and img.attrib['style'] != '':
            styles.append(re.sub(r';$', '', img.attrib['style']))
        if width:
            styles.append("max-width:"+width)
        if height:
            styles.append("max-height:"+height)

        if styles:
            img.attrib['style'] = ";".join(styles)
            img.attrib['width'] = '100%'
            if 'height' in img.attrib:
                img.attrib.pop('height')

        img.attrib['alt'] = alt
        img.attrib['title'] = title

        diag_tag = etree.tostring(img, short_empty_elements=self_closed).decode()
        diag_tag = diag_tag + map_tag

        return (
            text[:m.start()] + m.group('indent') + diag_tag + text[m.end():],
            m.start() + len(m.group('indent')) + len(diag_tag)
        )

    def _render_diagram(self, code):
        """Render the Diagram"""
        code = code.encode('utf8')


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
