"""
Tests for the dynamic stylesheet system
"""

import pytest
from PyQt5.QtGui import QColor
import mu.theming


def test_Stylesheet_get():
    sheet = mu.theming.Stylesheet()
    sheet.vars = {"test": QColor("red")}
    assert sheet["test"] == QColor("red")


def test_Stylesheet_set():
    sheet = mu.theming.Stylesheet()
    sheet["test"] = QColor("red")
    assert sheet.vars == {"test": QColor("red")}
    with pytest.raises(TypeError):
        sheet["type"] = "not a qcolor"


def test_Stylesheet_colours():
    sheet = mu.theming.Stylesheet()
    sheet["test"] = QColor("red")
    assert sheet.colours == {"test": "#ff0000"}
