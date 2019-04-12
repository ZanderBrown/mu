"""
Theme and presentation related code for the Mu editor.

Copyright (c) 2015-2019 Nicholas H.Tollervey and others (see the AUTHORS file).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import platform

from PyQt5.QtGui import QColor, QFontDatabase
from mu.resources import load_font_data
from mu.theming import Stylesheet


logger = logging.getLogger(__name__)

CHARTS = True
try:  # pragma: no cover
    from PyQt5.QtChart import QChart
except ImportError:  # pragma: no cover
    CHARTS = False


def should_patch_osx_mojave_font():
    """
    OSX mojave and qt5/qtscintilla has a bug where non-system installed fonts
    are always rendered as black, regardless of the theme color.

    This is inconvenient for light themes, but makes dark themes unusable.

    Using a system-installed font doesn't exhibit this behaviour, so
    update FONT_NAME to use the default terminal font in OSX on mojave.

    This patch should be removed once the underlying issue has been resolved

    github issue #552
    """
    return platform.platform().startswith("Darwin-18.")


# The default font size.
DEFAULT_FONT_SIZE = 14
# All editor windows use the same font
if should_patch_osx_mojave_font():  # pragma: no cover
    logger.warning("Overriding built-in editor font due to Issue #552")
    FONT_NAME = "Monaco"
else:  # pragma: no cover
    FONT_NAME = "Source Code Pro"

FONT_FILENAME_PATTERN = "SourceCodePro-{variant}.otf"
FONT_VARIANTS = ("Bold", "BoldIt", "It", "Regular", "Semibold", "SemiboldIt")
CUSTOM_DEFAULTS = {
    "BORDER": "#b4b4b4",
    "HOVER": "#cccccc",
    "CLOSE": "#e97867",
    "FOREGROUND": "#000000",
    "BACKGROUND": "#eeeeee",
    "EDITOR-BACKGROUND": "#fefee7",
    "EDITOR-FOREGROUND": "#181818",
    "CONTROL": "#c4c4c4",
    "TAB-CURRENT": "#e0e0e0",
    "FOCUS": "#0f53e7",
}

logger = logging.getLogger(__name__)


class Font:
    """
    Utility class that makes it easy to set font related values within the
    editor.
    """

    _DATABASE = None

    def __init__(
        self, color="#181818", paper="#FEFEF7", bold=False, italic=False
    ):
        self.color = color
        self.paper = paper
        self.bold = bold
        self.italic = italic

    @classmethod
    def get_database(cls):
        """
        Create a font database and load the MU builtin fonts into it.
        This is a cached classmethod so the font files aren't re-loaded
        every time a font is refereced
        """
        if cls._DATABASE is None:
            cls._DATABASE = QFontDatabase()
            for variant in FONT_VARIANTS:
                filename = FONT_FILENAME_PATTERN.format(variant=variant)
                font_data = load_font_data(filename)
                cls._DATABASE.addApplicationFontFromData(font_data)
        return cls._DATABASE

    def load(self, size=DEFAULT_FONT_SIZE):
        """
        Load the font from the font database, using the correct size and style
        """
        return Font.get_database().font(FONT_NAME, self.stylename, size)

    @property
    def stylename(self):
        """
        Map the bold and italic boolean flags here to a relevant
        font style name.
        """
        if self.bold:
            if self.italic:
                return "Semibold Italic"
            return "Semibold"
        if self.italic:
            return "Italic"
        return "Regular"


class Theme:
    """
    Defines a font and other theme specific related information.
    """

    name = "base"

    @classmethod
    def apply_to(cls, lexer):
        # Apply a font for all styles
        lexer.setFont(Font().load())

        for name, font in cls.__dict__.items():
            if not isinstance(font, Font):
                continue
            style_num = getattr(lexer, name)
            lexer.setColor(QColor(font.color), style_num)
            lexer.setEolFill(True, style_num)
            lexer.setPaper(QColor(font.paper), style_num)
            lexer.setFont(font.load(), style_num)

    def merge_dict(self, a, b):
        res = a
        for key, value in b.items():
            if key not in a or a[key] != value:
                res[key] = value
        return res

    @property
    def chart(self):
        if CHARTS:
            return QChart.ChartThemeLight
        else:
            return None


class DayTheme(Theme):
    """
    Defines a Python related theme including the various font colours for
    syntax highlighting.

    This is a light theme.
    """

    name = "day"
    icon = "theme_day"

    FunctionMethodName = ClassName = Font(color="#0000a0")
    UnclosedString = Font(paper="#FFDDDD")
    Comment = CommentBlock = Font(color="gray")
    Keyword = Font(color="#005050", bold=True)
    SingleQuotedString = DoubleQuotedString = Font(color="#800000")
    TripleSingleQuotedString = TripleDoubleQuotedString = Font(color="#060")
    Number = Font(color="#00008B")
    Decorator = Font(color="#cc6600")
    Default = Identifier = Font()
    Operator = Font(color="#400040")
    HighlightedIdentifier = Font(color="#0000a0")
    Paper = QColor("#FEFEF7")
    Caret = QColor("#181818")
    Margin = QColor("#EEE")
    IndicatorError = QColor("red")
    IndicatorStyle = QColor("blue")
    DebugStyle = QColor("#ffcc33")
    IndicatorWordMatch = QColor("lightGrey")
    BraceBackground = QColor("lightGrey")
    BraceForeground = QColor("blue")
    UnmatchedBraceBackground = QColor("#FFDDDD")
    UnmatchedBraceForeground = QColor("black")
    BreakpointMarker = QColor("#D80000")
    # HTML
    Tag = Keyword
    UnknownTag = Tag
    XMLTagEnd = Tag
    XMLStart = Tag
    XMLEnd = Tag
    Attribute = ClassName
    UnknownAttribute = Attribute
    HTMLNumber = Number
    HTMLDoubleQuotedString = DoubleQuotedString
    HTMLSingleQuotedString = SingleQuotedString
    OtherInTag = Default
    HTMLComment = Comment
    Entity = Operator
    CDATA = Decorator
    # CSS
    ClassSelector = Tag
    PseudoClass = ClassSelector
    UnknownPseudoClass = ClassSelector
    CSS1Property = (
        CSS2Property
    ) = CSS3Property = UnknownProperty = SingleQuotedString
    Value = Number
    IDSelector = Tag
    Important = UnmatchedBraceBackground
    AtRule = Decorator
    MediaRule = Decorator
    Variable = HighlightedIdentifier
    colours = {
        "BORDER": "#b4b4b4",
        "HOVER": "#cccccc",
        "CLOSE": "#e97867",
        "FOREGROUND": "#000000",
        "BACKGROUND": "#eeeeee",
        "EDITOR-BACKGROUND": "#FEFEF7",
        "EDITOR-FOREGROUND": "#181818",
        "CONTROL": "#c4c4c4",
        "TAB-CURRENT": "#e0e0e0",
        "FOCUS": "#0f53e7",
    }

    @property
    def stylesheet(self):
        sheet = Stylesheet()
        sheet.load("base.css")
        sheet.load("day.css")
        sheet.colours = self.colours
        return sheet


class NightTheme(Theme):
    """
    Defines a Python related theme including the various font colours for
    syntax highlighting.

    This is the dark theme.
    """

    name = "night"
    icon = "theme"

    FunctionMethodName = ClassName = Font(color="#81a2be", paper="#222")
    UnclosedString = Font(paper="#c93827")
    Comment = CommentBlock = CommentLine = Font(color="#969896", paper="#222")
    Keyword = Font(color="#73a46a", bold=True, paper="#222")
    SingleQuotedString = DoubleQuotedString = Font(
        color="#f0c674", paper="#222"
    )
    TripleSingleQuotedString = TripleDoubleQuotedString = Font(
        color="#f0c674", paper="#222"
    )
    Number = Font(color="#b5bd68", paper="#222")
    Decorator = Font(color="#cc6666", paper="#222")
    Default = Identifier = Font(color="#DDD", paper="#222")
    Operator = Font(color="#b294bb", paper="#222")
    HighlightedIdentifier = Font(color="#de935f", paper="#222")
    Paper = QColor("#222")
    Caret = QColor("#c6c6c6")
    Margin = QColor("#424446")
    IndicatorError = QColor("#c93827")
    IndicatorStyle = QColor("#2f5692")
    DebugStyle = QColor("#444")
    IndicatorWordMatch = QColor("#f14721")
    BraceBackground = QColor("#ed1596")
    BraceForeground = QColor("#222")
    UnmatchedBraceBackground = QColor("#c93827")
    UnmatchedBraceForeground = QColor("#222")
    BreakpointMarker = QColor("#c93827")
    # HTML
    Tag = Keyword
    UnknownTag = Tag
    XMLTagEnd = Tag
    XMLStart = Tag
    XMLEnd = Tag
    Attribute = ClassName
    UnknownAttribute = Attribute
    HTMLNumber = Number
    HTMLDoubleQuotedString = DoubleQuotedString
    HTMLSingleQuotedString = SingleQuotedString
    OtherInTag = Default
    HTMLComment = Comment
    Entity = Operator
    CDATA = Decorator
    # CSS
    ClassSelector = Tag
    PseudoClass = ClassSelector
    UnknownPseudoClass = ClassSelector
    CSS1Property = (
        CSS2Property
    ) = CSS3Property = UnknownProperty = SingleQuotedString
    Value = Number
    IDSelector = Tag
    Important = UnmatchedBraceBackground
    AtRule = Decorator
    MediaRule = Decorator
    Variable = HighlightedIdentifier
    colours = {
        "BORDER": "#6b6b6b",
        "HOVER": "#5c5c5c",
        "CLOSE": "#c93827",
        "FOREGROUND": "#FFFFFF",
        "BACKGROUND": "#222222",
        "EDITOR-BACKGROUND": "#373737",
        "EDITOR-FOREGROUND": "#FFFFFF",
        "CONTROL": "#474747",
        "TAB-CURRENT": "#6b6b6b",
        "FOCUS": "#929292",
    }

    @property
    def stylesheet(self):
        sheet = Stylesheet()
        sheet.load("base.css")
        sheet.load("night.css")
        sheet.colours = self.colours
        return sheet

    @property
    def chart(self):
        if CHARTS:
            return QChart.ChartThemeDark
        else:
            return None


class ContrastTheme(Theme):
    """
    Defines a Python related theme including the various font colours for
    syntax highlighting.

    This is the high contrast theme.
    """

    name = "contrast"
    icon = "theme_contrast"

    FunctionMethodName = ClassName = Font(color="#AAA", paper="black")
    UnclosedString = Font(paper="#666")
    Comment = CommentBlock = Font(color="#AAA", paper="black")
    Keyword = Font(color="#EEE", bold=True, paper="black")
    SingleQuotedString = DoubleQuotedString = Font(color="#AAA", paper="black")
    TripleSingleQuotedString = TripleDoubleQuotedString = Font(
        color="#AAA", paper="black"
    )
    Number = Font(color="#AAA", paper="black")
    Decorator = Font(color="#cccccc", paper="black")
    Default = Identifier = Font(color="#fff", paper="black")
    Operator = Font(color="#CCC", paper="black")
    HighlightedIdentifier = Font(color="#ffffff", paper="black")
    Paper = QColor("black")
    Caret = QColor("white")
    Margin = QColor("#333")
    IndicatorError = QColor("white")
    IndicatorStyle = QColor("cyan")
    DebugStyle = QColor("#666")
    IndicatorWordMatch = QColor("grey")
    BraceBackground = QColor("white")
    BraceForeground = QColor("black")
    UnmatchedBraceBackground = QColor("#666")
    UnmatchedBraceForeground = QColor("black")
    BreakpointMarker = QColor("lightGrey")
    # HTML
    Tag = Keyword
    UnknownTag = Tag
    XMLTagEnd = Tag
    XMLStart = Tag
    XMLEnd = Tag
    Attribute = ClassName
    UnknownAttribute = Attribute
    HTMLNumber = Number
    HTMLDoubleQuotedString = DoubleQuotedString
    HTMLSingleQuotedString = SingleQuotedString
    OtherInTag = Default
    HTMLComment = Comment
    Entity = Operator
    CDATA = Decorator
    # CSS
    ClassSelector = Tag
    PseudoClass = ClassSelector
    UnknownPseudoClass = ClassSelector
    CSS1Property = (
        CSS2Property
    ) = CSS3Property = UnknownProperty = SingleQuotedString
    Value = Number
    IDSelector = Tag
    Important = UnmatchedBraceBackground
    AtRule = Decorator
    MediaRule = Decorator
    Variable = HighlightedIdentifier
    colours = {
        "BORDER": "#555555",
        "HOVER": "#888888",
        "CLOSE": "#c93827",
        "FOREGROUND": "#FFFFFF",
        "BACKGROUND": "#000000",
        "EDITOR-BACKGROUND": "#FFFFFF",
        "EDITOR-FOREGROUND": "#000000",
        "CONTROL": "#2e2e2e",
        "TAB-CURRENT": "#555555",
        "FOCUS": "yellow",
    }

    @property
    def stylesheet(self):
        sheet = Stylesheet()
        sheet.load("base.css")
        sheet.load("contrast.css")
        sheet.colours = self.colours
        return sheet

    @property
    def chart(self):
        if CHARTS:
            return QChart.ChartThemeHighContrast
        else:
            return None


class CustomTheme(Theme):
    """
    Defines a Python related theme including the various font colours for
    syntax highlighting.

    This is the high contrast theme.
    """

    name = "custom"
    icon = "theme_custom"

    FunctionMethodName = ClassName = Font(color="#0000a0")
    UnclosedString = Font(paper="#FFDDDD")
    Comment = CommentBlock = Font(color="gray")
    Keyword = Font(color="#005050", bold=True)
    SingleQuotedString = DoubleQuotedString = Font(color="#800000")
    TripleSingleQuotedString = TripleDoubleQuotedString = Font(color="#060")
    Number = Font(color="#00008B")
    Decorator = Font(color="#cc6600")
    Default = Identifier = Font()
    Operator = Font(color="#400040")
    HighlightedIdentifier = Font(color="#0000a0")
    Paper = QColor("#FEFEF7")
    Caret = QColor("#181818")
    Margin = QColor("#EEE")
    IndicatorError = QColor("red")
    IndicatorStyle = QColor("blue")
    DebugStyle = QColor("#ffcc33")
    IndicatorWordMatch = QColor("lightGrey")
    BraceBackground = QColor("lightGrey")
    BraceForeground = QColor("blue")
    UnmatchedBraceBackground = QColor("#FFDDDD")
    UnmatchedBraceForeground = QColor("black")
    BreakpointMarker = QColor("#D80000")
    # HTML
    Tag = Keyword
    UnknownTag = Tag
    XMLTagEnd = Tag
    XMLStart = Tag
    XMLEnd = Tag
    Attribute = ClassName
    UnknownAttribute = Attribute
    HTMLNumber = Number
    HTMLDoubleQuotedString = DoubleQuotedString
    HTMLSingleQuotedString = SingleQuotedString
    OtherInTag = Default
    HTMLComment = Comment
    Entity = Operator
    CDATA = Decorator
    # CSS
    ClassSelector = Tag
    PseudoClass = ClassSelector
    UnknownPseudoClass = ClassSelector
    CSS1Property = (
        CSS2Property
    ) = CSS3Property = UnknownProperty = SingleQuotedString
    Value = Number
    IDSelector = Tag
    Important = UnmatchedBraceBackground
    AtRule = Decorator
    MediaRule = Decorator
    Variable = HighlightedIdentifier
    colours = {}

    @property
    def stylesheet(self):
        sheet = Stylesheet()
        sheet.load("base.css")
        sheet.colours = self.merge_dict(CUSTOM_DEFAULTS, self.colours)
        return sheet
