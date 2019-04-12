# -*- coding: utf-8 -*-
"""
Tests for the user interface elements of Mu.
"""
from unittest import mock
import mu.interface.themes
import mu.interface.editor


def test_patch_osx_mojave_font_issue_552():
    with mock.patch("platform.platform", return_value="Windows"):
        assert not mu.interface.themes.should_patch_osx_mojave_font()
    with mock.patch(
        "platform.platform", return_value="Darwin-18.0.0-x86_64-i386-64bit"
    ):
        assert mu.interface.themes.should_patch_osx_mojave_font()


def test_Font():
    """
    Ensure the Font class works as expected with default and passed in args.
    """
    f = mu.interface.themes.Font()
    # Defaults
    assert f.color == "#181818"
    assert f.paper == "#FEFEF7"
    assert f.bold is False
    assert f.italic is False
    # Passed in arguments
    f = mu.interface.themes.Font(
        color="pink", paper="black", bold=True, italic=True
    )
    assert f.color == "pink"
    assert f.paper == "black"
    assert f.bold
    assert f.italic


def test_theme_apply_to():
    """
    Ensure that the apply_to class method updates the passed in lexer with the
    expected font settings.
    """
    lexer = mu.interface.editor.PythonLexer()
    theme = mu.interface.themes.DayTheme()
    lexer.setFont = mock.MagicMock(return_value=None)
    lexer.setColor = mock.MagicMock(return_value=None)
    lexer.setEolFill = mock.MagicMock(return_value=None)
    lexer.setPaper = mock.MagicMock(return_value=None)
    theme.apply_to(lexer)
    assert lexer.setFont.call_count == 17
    assert lexer.setColor.call_count == 16
    assert lexer.setEolFill.call_count == 16
    assert lexer.setPaper.call_count == 16


def test_Theme_merge_dict():
    """
    Merged dictionaries should contain the elements
    of both dicts with the second overriding the first
    """
    theme = mu.interface.themes.Theme()
    # Merge with only unique elements
    a = {"a": 1}
    b = {"b": 2}
    c = theme.merge_dict(a, b)
    assert c == {"a": 1, "b": 2}
    # Merge with duplicate elements
    a = {"a": 1, "b": 3}
    b = {"b": 2}
    c = theme.merge_dict(a, b)
    assert c == {"a": 1, "b": 2}


def test_Theme_chart():
    """
    Should specify the default theme when charts are enabled
    """
    theme = mu.interface.themes.Theme()
    with mock.patch("mu.interface.themes.CHARTS", True):
        charts = mock.MagicMock()
        charts.ChartThemeLight = mock.MagicMock()
        with mock.patch("mu.interface.themes.QChart", charts):
            assert theme.chart == charts.ChartThemeLight
    with mock.patch("mu.interface.themes.CHARTS", False):
        assert theme.chart is None


def test_NightTheme_chart():
    """
    Should specify the light theme when charts are enabled
    """
    theme = mu.interface.themes.NightTheme()
    with mock.patch("mu.interface.themes.CHARTS", True):
        charts = mock.MagicMock()
        charts.ChartThemeDark = mock.MagicMock()
        with mock.patch("mu.interface.themes.QChart", charts):
            assert theme.chart == charts.ChartThemeDark
    with mock.patch("mu.interface.themes.CHARTS", False):
        assert theme.chart is None


def test_ContrastTheme_chart():
    """
    Should specify the high contrast theme when charts are enabled
    """
    theme = mu.interface.themes.ContrastTheme()
    with mock.patch("mu.interface.themes.CHARTS", True):
        charts = mock.MagicMock()
        charts.ChartThemeHighContrast = mock.MagicMock()
        with mock.patch("mu.interface.themes.QChart", charts):
            assert theme.chart == charts.ChartThemeHighContrast
    with mock.patch("mu.interface.themes.CHARTS", False):
        assert theme.chart is None


def test_Font_loading():
    with mock.patch("mu.interface.themes.FONT_NAME", "Source Code Pro"):
        mu.interface.themes.Font._DATABASE = None
        try:
            with mock.patch("mu.interface.themes.QFontDatabase") as db:
                mu.interface.themes.Font().load()
                mu.interface.themes.Font(bold=True).load()
                mu.interface.themes.Font(italic=True).load()
                mu.interface.themes.Font(bold=True, italic=True).load()
        finally:
            mu.interface.themes.Font._DATABASE = None
        db.assert_called_once_with()
        db().font.assert_has_calls(
            [
                mock.call("Source Code Pro", "Regular", 14),
                mock.call("Source Code Pro", "Semibold", 14),
                mock.call("Source Code Pro", "Italic", 14),
                mock.call("Source Code Pro", "Semibold Italic", 14),
            ]
        )
