# [Schemdraw](https://bitbucket.org/cdelker/schemdraw/src/master/) Extension for [Python-Markdown](https://python-markdown.github.io/)
*a simpler way to document circuits in markdown*

**Inspiration:** This project is inspired by the wonderful project:
[`plantuml-markdown`](https://github.com/mikitex70/plantuml-markdown). So,
shoutout to the folks who've toiled on that project to make it great!

## Usage

This package allows you to configure a schematic drawing, directly in markdown
using a code-fenced sample as follows:

```
::schemdraw:: alt="My super diagram"
    += elm.Resistor().right().label('1Ω')
    += elm.Capacitor().down().label('10μF')
    += elm.Line().left()
    += elm.SourceSin().up().label('10V')
::end-schemdraw::
```

## Security Note

This package makes use of Python's `exec` functionality, which is inherently
somewhat insecure, as it allows for arbitrary code execution. Only carfully
curated drawings logic should be used.

## Installation


#### Installing from Source

1. Clone Repository
2. From within local Repository folder, issue:

```shell
pip install .
```
