"""
Theme colouring panel for admin dialog

Copyright (c) 2018 Nicholas H.Tollervey and others (see the AUTHORS file).

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
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget,
    QPushButton,
    QColorDialog,
)

logger = logging.getLogger(__name__)


class ColourButton(QPushButton):
    """
    Button for picking a colour
    """

    def __init__(self, parent, colour):
        super().__init__(parent)
        # Cache the inital colour
        self._colour = colour
        # We create dialogs as needed
        self.dlg = None
        # Respond to clicks
        self.clicked.connect(self.activated)

        # Format string for setting background
        self.sheet = "QPushButton {{ background: {}; }} "
        # Set initial colour
        self.preview(colour)

    def activated(self, checked=None):
        # If we haven't already show a dialog
        if not self.dlg:
            # Create one
            self.dlg = QColorDialog(self)
            self.dlg.currentColorChanged.connect(self.preview)
            self.dlg.setCurrentColor(self._colour)
        # Show the dialog
        self.dlg.exec()

    def preview(self, colour):
        """
        Set the background of the button
        """
        self.setStyleSheet(self.sheet.format(colour.name()))

    @property
    def colour(self):
        """
        Either the inital colour or selected colour
        """
        if self.dlg:
            return self.dlg.selectedColor().name()
        # Should handle default colours better
        return self._colour.name()

    @colour.setter
    def colour(self, val):
        col = QColor(val)
        self._colour = col
        self.preview(col)
        if self.dlg:
            self.dlg.setCurrentColor(col)


class ColourWidget(QWidget):
    """
    Configure colours
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(3, 1)
        self.setLayout(self.layout)
        # Foreground
        col = QColor(255, 0, 0)
        self.foreground = self.add_button(0, 0, _("Foreground"), col)
        # Background
        col = QColor(0, 255, 0)
        self.background = self.add_button(0, 2, _("Background"), col)
        # Editor Text
        col = QColor(0, 255, 0)
        self.editor_fore = self.add_button(1, 0, _("Editor Text"), col)
        # Editor Background
        col = QColor(0, 255, 0)
        self.editor_back = self.add_button(1, 2, _("Editor Background"), col)
        # Border
        col = QColor(0, 0, 255)
        self.border = self.add_button(2, 0, _("Border"), col)
        # Control
        col = QColor(0, 255, 0)
        self.control = self.add_button(2, 2, _("Buttons"), col)
        # Hover
        col = QColor(0, 255, 0)
        self.hover = self.add_button(3, 0, _("Hover"), col)
        # Focus
        col = QColor(0, 255, 0)
        self.focus = self.add_button(3, 2, _("Focus"), col)
        # Current Tab
        col = QColor(0, 255, 0)
        self.tab_current = self.add_button(4, 0, _("Current Tab"), col)
        # Close
        col = QColor(0, 255, 0)
        self.close = self.add_button(4, 2, _("Close"), col)

    def add_button(self, row, col, label, current):
        btn = ColourButton(self, current)
        self.layout.addWidget(btn, row, col, Qt.AlignLeft)
        lbl = QLabel(label)
        self.layout.addWidget(lbl, row, col + 1, Qt.AlignLeft)
        return btn

    def get_colours(self, default):
        res = {}

        # TODO: Find a less verbose way to do this
        if self.background.colour != default["BACKGROUND"]:
            res["BACKGROUND"] = self.background.colour

        if self.foreground.colour != default["FOREGROUND"]:
            res["FOREGROUND"] = self.foreground.colour

        if self.editor_back.colour != default["EDITOR-BACKGROUND"]:
            res["EDITOR-BACKGROUND"] = self.editor_back.colour

        if self.editor_fore.colour != default["EDITOR-FOREGROUND"]:
            res["EDITOR-FOREGROUND"] = self.editor_fore.colour

        if self.border.colour != default["BORDER"]:
            res["BORDER"] = self.border.colour

        if self.control.colour != default["CONTROL"]:
            res["CONTROL"] = self.control.colour

        if self.hover.colour != default["HOVER"]:
            res["HOVER"] = self.hover.colour

        if self.focus.colour != default["FOCUS"]:
            res["FOCUS"] = self.focus.colour

        if self.tab_current.colour != default["TAB-CURRENT"]:
            res["TAB-CURRENT"] = self.tab_current.colour

        if self.close.colour != default["CLOSE"]:
            res["CLOSE"] = self.close.colour

        return res

    def set_colours(self, colours, fallback):
        self.background.colour = self.get_colour(
            colours, fallback, "BACKGROUND"
        )
        self.foreground.colour = self.get_colour(
            colours, fallback, "FOREGROUND"
        )
        self.editor_back.colour = self.get_colour(
            colours, fallback, "EDITOR-BACKGROUND"
        )
        self.editor_fore.colour = self.get_colour(
            colours, fallback, "EDITOR-FOREGROUND"
        )
        self.border.colour = self.get_colour(colours, fallback, "BORDER")
        self.control.colour = self.get_colour(colours, fallback, "CONTROL")
        self.hover.colour = self.get_colour(colours, fallback, "HOVER")
        self.focus.colour = self.get_colour(colours, fallback, "FOCUS")
        self.tab_current.colour = self.get_colour(
            colours, fallback, "TAB-CURRENT"
        )
        self.close.colour = self.get_colour(colours, fallback, "CLOSE")

    def get_colour(self, colours, fallback, name):
        colour = fallback[name]
        if name in colours and colours[name] != "[NONE]":
            colour = colours[name]
        return colour
