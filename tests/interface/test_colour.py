"""
Tests for colour panel of the admin dialog
"""
from unittest import mock
from PyQt5.QtGui import QColor
import mu.interface.colour
from mu.interface.themes import CUSTOM_DEFAULTS


def test_ColourButton_activated():
    btn = mu.interface.colour.ColourButton(None, "#ffffff")
    dlg = mock.MagicMock()
    with mock.patch("mu.interface.colour.QColorDialog", dlg):
        btn.activated()
        calls = [
            mock.call(btn),
            mock.call().currentColorChanged.connect(btn.preview),
            mock.call().setCurrentColor(btn._colour),
            mock.call().exec(),
        ]
        dlg.assert_has_calls(calls)


def test_ColourButton_activated_cached_dlg():
    btn = mu.interface.colour.ColourButton(None, "#ffffff")
    dlg_mock = mock.MagicMock()
    dlg_mock.exec = mock.MagicMock()
    btn.dlg = dlg_mock
    btn.activated()
    dlg_mock.exec.assert_called_once_with()


def test_ColourButton_preview():
    btn = mu.interface.colour.ColourButton(None, "#ffffff")
    btn.setStyleSheet = mock.MagicMock()
    btn.preview(QColor("#fefefe"))
    btn.setStyleSheet.assert_called_once_with(btn.sheet.format("#fefefe"))


def test_ColourButton_colour_getter():
    btn = mu.interface.colour.ColourButton(None, "#ffffff")
    assert btn.colour == "#ffffff"
    btn.dlg = mock.MagicMock()
    btn.dlg.selectedColor = mock.MagicMock(return_value=QColor("#3b3b3b"))
    assert btn.colour == "#3b3b3b"


def test_ColourButton_colour_setter():
    btn = mu.interface.colour.ColourButton(None, "#ffffff")
    btn.preview = mock.MagicMock()
    btn.colour = "#e4e4e4"
    btn.preview.assert_called_once_with(QColor("#e4e4e4"))
    btn.dlg = mock.MagicMock()
    btn.dlg.setCurrentColor = mock.MagicMock()
    btn.colour = "#d6d6d6"
    btn.dlg.setCurrentColor.assert_called_once_with(QColor("#d6d6d6"))


def test_ColourButton_context_menu():
    btn = mu.interface.colour.ColourButton(None, "#ffffff")
    mock_point = mock.MagicMock()
    btn.mapToGlobal = mock.MagicMock(return_value=mock_point)
    btn.reset = mock.MagicMock()
    event = mock.MagicMock()
    menu = mock.MagicMock()
    menu.addAction = mock.MagicMock(side_effect=[42])
    menu.exec_ = mock.MagicMock(side_effect=[42])
    menu_mock = mock.MagicMock(return_value=menu)
    with mock.patch("mu.interface.colour.QMenu", menu_mock):
        btn.contextMenuEvent(event)
        menu_mock.assert_called_once_with(btn)
        menu.addAction.assert_called_once_with(_("Reset"))
        menu.exec_.assert_called_once_with(mock_point)
        btn.reset.assert_called_once_with()


def test_ColourButton_reset():
    btn = mu.interface.colour.ColourButton(None, "#ffffff")
    btn.default = "#3e3e3e"
    btn.colour = "#e3e3e3"
    assert btn.default != btn.colour
    btn.reset()
    assert btn.default == btn.colour == "#3e3e3e"


def test_ColourWidget_reset():
    widget = mu.interface.colour.ColourWidget(None)
    testa = mu.interface.colour.ColourButton(widget, "#454545")
    testb = mu.interface.colour.ColourButton(widget, "#565656")
    widget.controls = {"TESTA": testa, "TESTB": testb}
    testa.colour = "#787878"
    testb.colour = "#898989"
    assert testa.colour != testa.default
    assert testb.colour != testb.default
    widget.reset()
    assert testa.colour == testa.default
    assert testb.colour == testb.default


def test_ColourWidget_get_colour():
    widget = mu.interface.colour.ColourWidget(None)
    control = CUSTOM_DEFAULTS["CONTROL"]
    assert widget.get_colour({}, "CONTROL") == control
    assert widget.get_colour({"CONTROL": "#3d3d3d"}, "CONTROL") == "#3d3d3d"
