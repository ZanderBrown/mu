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
from PyQt5.Qsci import QsciScintilla
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
        self,
        color="%:EDITOR-FOREGROUND:%",
        paper="%:EDITOR-BACKGROUND:%",
        bold=False,
        italic=False,
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
    colours = {
        "BORDER": "#b4b4b4",
        "HOVER": "#cccccc",
        "CLOSE": "#e97867",
        "FOREGROUND": "#000000",
        "BACKGROUND": "#eeeeee",
        "EDITOR-BACKGROUND": "#fefef7",
        "EDITOR-FOREGROUND": "#181818",
        "CONTROL": "#c4c4c4",
        "TAB-CURRENT": "#e0e0e0",
        "FOCUS": "#0f53e7",
    }
    fonts = {
        "FunctionMethodName,ClassName,Attribute,UnknownAttribute": Font(
            color="#0000a0"
        ),
        "UnclosedString": Font(paper="#FFDDDD"),
        "Comment,CommentBlock,HTMLComment": Font(color="gray"),
        "Keyword,Tag,UnknownTag,XMLTagEnd,XMLStart,XMLEnd,ClassSelector,"
        + "PseudoClass,UnknownPseudoClass,IDSelector": Font(
            color="#005050", bold=True
        ),
        "SingleQuotedString,DoubleQuotedString,HTMLSingleQuotedString,"
        + "HTMLDoubleQuotedString,CSS1Property,CSS2Property,"
        + "CSS3Property,UnknownProperty": Font(color="#800000"),
        "TripleSingleQuotedString,TripleDoubleQuotedString": Font(
            color="#060"
        ),
        "Number,HTMLNumber,Value": Font(color="#00008B"),
        "Decorator,CDATA,AtRule,MediaRule": Font(color="#cc6600"),
        "Default,Identifier,OtherInTag": Font(),
        "Operator,Entity": Font(color="#400040"),
        "HighlightedIdentifier,Variable": Font(color="#0000a0"),
    }
    default_font = Font()
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
    Important = UnmatchedBraceBackground

    def get_colour(self, name):
        return self.colours[name]

    def map_colour(self, colour):
        if colour.startswith("%:"):
            return QColor(self.get_colour(colour[2:-2]))
        return QColor(colour)

    def apply_to_editor(self, editor):
        # Apply a font for all styles
        editor.lexer.setFont(self.default_font.load())

        colour = self.map_colour(self.default_font.color)
        paper = self.map_colour(self.default_font.paper)

        editor.setColor(colour)
        editor.setPaper(paper)
        editor.lexer.setDefaultColor(colour)
        editor.lexer.setDefaultPaper(paper)

        # Iterate the fonts defined by the theme
        for names, font in self.fonts.items():
            # Some fonts are used for multiple properties
            # they a separated by commas
            for name in names.split(","):
                style_num = getattr(editor.lexer, name)
                editor.lexer.setColor(self.map_colour(font.color), style_num)
                editor.lexer.setEolFill(True, style_num)
                editor.lexer.setPaper(self.map_colour(font.paper), style_num)
                editor.lexer.setFont(font.load(), style_num)

        editor.setCaretForegroundColor(self.Caret)
        editor.setIndicatorForegroundColor(
            self.IndicatorError, editor.check_indicators["error"]["id"]
        )
        editor.setIndicatorForegroundColor(
            self.IndicatorStyle, editor.check_indicators["style"]["id"]
        )
        editor.setIndicatorForegroundColor(
            self.DebugStyle, editor.DEBUG_INDICATOR
        )
        for type_ in editor.search_indicators:
            editor.setIndicatorForegroundColor(
                self.IndicatorWordMatch, editor.search_indicators[type_]["id"]
            )
        editor.setMarkerBackgroundColor(
            self.BreakpointMarker, editor.BREAKPOINT_MARKER
        )
        editor.setAutoCompletionThreshold(2)
        editor.setAutoCompletionSource(QsciScintilla.AcsAll)
        editor.setLexer(editor.lexer)
        editor.setMarginsBackgroundColor(self.Margin)
        editor.setMarginsForegroundColor(self.Caret)
        editor.setMatchedBraceBackgroundColor(self.BraceBackground)
        editor.setMatchedBraceForegroundColor(self.BraceForeground)
        editor.setUnmatchedBraceBackgroundColor(self.UnmatchedBraceBackground)
        editor.setUnmatchedBraceForegroundColor(self.UnmatchedBraceForeground)

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
    fonts = {
        "FunctionMethodName,ClassName,Attribute,UnknownAttribute": Font(
            color="#81a2be"
        ),
        "UnclosedString": Font(paper="#c93827"),
        "Comment,CommentBlock,HTMLComment": Font(color="#969896"),
        "Keyword,Tag,UnknownTag,XMLTagEnd,XMLStart,XMLEnd,ClassSelector,"
        + "PseudoClass,UnknownPseudoClass,IDSelector": Font(
            color="#73a46a", bold=True
        ),
        "SingleQuotedString,DoubleQuotedString,HTMLSingleQuotedString,"
        + "HTMLDoubleQuotedString,CSS1Property,CSS2Property,"
        + "CSS3Property,UnknownProperty": Font(color="#f0c674"),
        "TripleSingleQuotedString,TripleDoubleQuotedString": Font(
            color="#f0c674"
        ),
        "Number,HTMLNumber,Value": Font(color="#b5bd68"),
        "Decorator,CDATA,AtRule,MediaRule": Font(color="#cc6666"),
        "Default,Identifier,OtherInTag": Font(color="#DDD"),
        "Operator,Entity": Font(color="#b294bb"),
        "HighlightedIdentifier,Variable": Font(color="#de935f"),
    }
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
    Important = UnmatchedBraceBackground

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
    fonts = {
        "FunctionMethodName,ClassName,Attribute,UnknownAttribute": Font(
            color="#AAA", paper="black"
        ),
        "UnclosedString": Font(paper="#666"),
        "Comment,CommentBlock,HTMLComment": Font(color="#AAA", paper="black"),
        "Keyword,Tag,UnknownTag,XMLTagEnd,XMLStart,XMLEnd,ClassSelector,"
        + "ClassSelector,UnknownPseudoClass,IDSelector": Font(
            color="#EEE", bold=True, paper="black"
        ),
        "SingleQuotedString,DoubleQuotedString,HTMLSingleQuotedString,"
        + "HTMLDoubleQuotedString,CSS1Property,CSS2Property,"
        + "CSS3Property,UnknownProperty": Font(color="#AAA", paper="black"),
        "TripleSingleQuotedString,TripleDoubleQuotedString": Font(
            color="#AAA", paper="black"
        ),
        "Number,HTMLNumber,Value": Font(color="#AAA", paper="black"),
        "Decorator,CDATA,AtRule,MediaRule": Font(
            color="#cccccc", paper="black"
        ),
        "Default,OtherInTag,Identifier": Font(color="#fff", paper="black"),
        "Operator,Entity": Font(color="#CCC", paper="black"),
        "HighlightedIdentifier,Variable": Font(color="#ffffff", paper="black"),
    }
    default_font = Font(paper="black")
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
    Important = UnmatchedBraceBackground

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

    This is the custom theme.
    """

    name = "custom"
    icon = "theme_custom"

    colours = {}

    @property
    def stylesheet(self):
        sheet = Stylesheet()
        sheet.load("base.css")
        sheet.colours = self.merge_dict(CUSTOM_DEFAULTS, self.colours)
        return sheet

    def get_colour(self, name):
        return self.merge_dict(CUSTOM_DEFAULTS, self.colours)[name]
