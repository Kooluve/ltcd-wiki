"""
preserve_blank_lines.py

A small Python-Markdown extension to preserve multiple consecutive blank lines
when rendering MkDocs documentation.

How it works
------------
- The extension looks for sequences of 3 or more consecutive newlines in the raw
  Markdown source (this corresponds to two or more *empty* lines between text
  blocks).
- Each matched sequence is replaced by a standalone HTML block
  (`<div class="mkdocs-preserved-blank" style="height:..."></div>`)
  whose inline height is computed from the number of blank lines.

Why 3+ newlines?
- Standard Markdown treats two consecutive newlines (`\n\n`) as the paragraph
  separator. We only act on sequences of 3+ newlines to avoid changing the
  normal paragraph behavior and only handle "extra" blank lines.

Installation (quick)
--------------------
1. Put this file in your MkDocs project root (the same folder as `mkdocs.yml`).
   Example: `preserve_blank_lines.py` next to `mkdocs.yml`.
2. Edit `mkdocs.yml` and add the extension (example):

   markdown_extensions:
     - preserve_blank_lines:
         height_per_blank: 1   # numeric, default: 1
         unit: em              # css unit, default: 'em'
         max_blanks: 50        # optional clamp to avoid huge gaps

3. Run `mkdocs serve` or `mkdocs build` as usual. The extension will be found
   because MkDocs runs with the project root on `sys.path`.

Configuration
-------------
- `height_per_blank` (number): how many `unit`s each blank line should add.
  Default: 1
- `unit` (string): CSS unit to use. Default: `em` (you can use `px`, `rem` etc.)
- `max_blanks` (int): maximum number of blank lines to convert (safety clamp).

Notes
-----
- This extension injects a standalone HTML block for each multi-blank sequence.
  Markdown will pass that HTML through unchanged, so styles are applied as-is.
- If you prefer to provide styling centrally instead of inline styles, you can
  replace the `style` attribute in the code with a class and add CSS in your
  theme's extra CSS.

If you want a slightly different behavior (for example: treat 2+ newlines as
preservable, or use a multiple of line-height instead of a fixed unit), tell
me and I'll adjust the code.

"""

from __future__ import annotations

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re
from typing import List

# Match three or more consecutive newlines (Unix \n and Windows \r\n allowed)
_RE_BLANKS = re.compile(r'(?:\r?\n){3,}')

class PreserveBlankLinesPreprocessor(Preprocessor):
    """Preprocessor that replaces long runs of newlines with a sized HTML block.

    It expects to receive the document as a list of lines and returns a list of
    lines. The replacement is a standalone HTML block so Markdown passes it
    through unchanged.
    """
    def __init__(self, md, height_per_blank: float = 1.0, unit: str = 'em', max_blanks: int = 50):
        super().__init__(md)
        try:
            self.height_per_blank = float(height_per_blank)
        except Exception:
            self.height_per_blank = 1.0
        self.unit = str(unit or 'em')
        try:
            self.max_blanks = int(max_blanks)
        except Exception:
            self.max_blanks = 50

    def run(self, lines: List[str]) -> List[str]:
        text = '\n'.join(lines)

        def _repl(m: re.Match) -> str:
            # number of newlines in the match
            n_newlines = m.group(0).count('\n')
            # visible blank lines between text blocks ~= newlines - 1
            blanks = max(0, n_newlines - 1)
            blanks = min(blanks, self.max_blanks)

            if blanks <= 0:
                return '\n\n'

            height_value = self.height_per_blank * blanks
            # Format height compactly (no trailing .0 when integer)
            if float(height_value).is_integer():
                height_str = f"{int(height_value)}{self.unit}"
            else:
                height_str = f"{height_value}{self.unit}"

            # Standalone HTML block so Markdown leaves it untouched
            return f"\n\n<div class=\"mkdocs-preserved-blank\" style=\"height:{height_str};line-height:0;margin:0;padding:0\"></div>\n\n"

        text = _RE_BLANKS.sub(_repl, text)
        return text.split('\n')


class PreserveBlankLinesExtension(Extension):
    """Python-Markdown extension wrapper exposing simple config options."""
    def __init__(self, **kwargs):
        self.config = {
            'height_per_blank': [1, 'height per blank line (numeric)'],
            'unit': ['em', 'CSS unit (em, rem, px, etc.)'],
            'max_blanks': [50, 'maximum number of blank lines to convert'],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        height = self.getConfig('height_per_blank')
        unit = self.getConfig('unit')
        max_blanks = self.getConfig('max_blanks')
        md.preprocessors.register(
            PreserveBlankLinesPreprocessor(md, height_per_blank=height, unit=unit, max_blanks=max_blanks),
            'preserve_blank_lines',
            175,
        )


def makeExtension(**kwargs):
    return PreserveBlankLinesExtension(**kwargs)


__all__ = ['PreserveBlankLinesExtension', 'makeExtension']
