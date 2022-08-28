# schemdraw-markdown
*a simpler way to document simple circuits in markdown*

[schemdraw](https://bitbucket.org/cdelker/schemdraw/src/master/) in markdown
files.

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
