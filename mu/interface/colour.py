"""
Theme colouring panel for admin dialog

Copyright (c) 2019 Nicholas H.Tollervey and others (see the AUTHORS file).

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
    QMenu,
    QWidget,
    QPushButton,
    QColorDialog,
)
from mu.interface.themes import CUSTOM_DEFAULTS

logger = logging.getLogger(__name__)


class ColourButton(QPushButton):
    """
    Button for picking a colour
    """

    def __init__(self, parent, default):
        super().__init__(parent)
        # Cache the inital colour
        self._colour = None
        # The default colour
        self.default = default
        # We create dialogs as needed
        self.dlg = None
        # Respond to clicks
        self.clicked.connect(self.activated)

        # Format string for setting background
        self.sheet = "QPushButton {{ background: {}; }} "

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

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        reset_action = menu.addAction(_("Reset"))
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == reset_action:
            self.reset()

    def reset(self):
        self.colour = self.default


class ColourWidget(QWidget):
    """
    Configure colours
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.controls = {}
        self.layout = QGridLayout()
        self.layout.setColumnStretch(3, 1)
        self.layout.setRowStretch(5, 1)
        self.layout.setHorizontalSpacing(16)
        self.layout.setVerticalSpacing(8)
        self.setLayout(self.layout)

        label = QLabel(_("Colours used with the custom theme"))
        self.layout.addWidget(label, 0, 0, 1, 3, Qt.AlignLeft)

        reset = QPushButton(_("Reset colours"))
        reset.clicked.connect(self.reset)
        self.layout.addWidget(reset, 0, 3, Qt.AlignRight)

        self.add_button(1, 0, _("Foreground"), "FOREGROUND")
        self.add_button(1, 2, _("Background"), "BACKGROUND")
        self.add_button(2, 0, _("Editor Text"), "EDITOR-FOREGROUND")
        self.add_button(2, 2, _("Editor Background"), "EDITOR-BACKGROUND")
        self.add_button(3, 0, _("Border"), "BORDER")
        self.add_button(3, 2, _("Buttons"), "CONTROL")
        self.add_button(4, 0, _("Hover"), "HOVER")
        self.add_button(4, 2, _("Focus"), "FOCUS")
        self.add_button(5, 0, _("Current Tab"), "TAB-CURRENT")
        self.add_button(5, 2, _("Close"), "CLOSE")

    def reset(self):
        for btn in self.controls.values():
            btn.reset()

    def add_button(self, row, col, label, key):
        btn = ColourButton(self, CUSTOM_DEFAULTS[key])
        self.layout.addWidget(btn, row, col, Qt.AlignLeft)
        lbl = QLabel(label)
        self.layout.addWidget(lbl, row, col + 1, Qt.AlignLeft)
        self.controls[key] = btn
        return btn

    def get_colours(self):
        res = {}

        for key in self.controls.keys():
            res[key] = self.controls[key].colour

        return res

    def set_colours(self, colours):
        for key in self.controls.keys():
            self.controls[key].colour = self.get_colour(colours, key)

    def get_colour(self, colours, name):
        colour = CUSTOM_DEFAULTS[name]
        if name in colours and colours[name] != "[NONE]":
            colour = colours[name]
        return colour
