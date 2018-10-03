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

    def __init__(self, parent):
        super().__init__(parent)
        # Cache the inital colour
        self._colour = None
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


class ColourWidget(QWidget):
    """
    Configure colours
    """

    def __init__(self, parent, default):
        super().__init__(parent)
        self.controls = []
        self.default = default
        self.layout = QGridLayout()
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(3, 1)
        self.setLayout(self.layout)
        self.add_button(0, 0, _("Foreground"), "FOREGROUND")
        self.add_button(0, 2, _("Background"), "BACKGROUND")
        self.add_button(1, 0, _("Editor Text"), "EDITOR-FOREGROUND")
        self.add_button(1, 2, _("Editor Background"), "EDITOR-BACKGROUND")
        self.add_button(2, 0, _("Border"), "BORDER")
        self.add_button(2, 2, _("Buttons"), "CONTROL")
        self.add_button(3, 0, _("Hover"), "HOVER")
        self.add_button(3, 2, _("Focus"), "FOCUS")
        self.add_button(4, 0, _("Current Tab"), "TAB-CURRENT")
        self.add_button(4, 2, _("Close"), "CLOSE")
        reset = QPushButton("Restore Defaults")
        reset.clicked.connect(self.reset)
        self.layout.addWidget(reset, 5, 3, Qt.AlignRight)

    def reset(self):
        for btn, id in self.controls:
            btn.colour = self.default[id]

    def add_button(self, row, col, label, id):
        btn = ColourButton(self)
        self.layout.addWidget(btn, row, col, Qt.AlignLeft)
        lbl = QLabel(label)
        self.layout.addWidget(lbl, row, col + 1, Qt.AlignLeft)
        self.controls.append((btn, id))
        return btn

    def get_colours(self):
        res = {}

        for btn, id in self.controls:
            if btn.colour != self.default[id]:
                res[id] = btn.colour

        return res

    def set_colours(self, colours):
        for btn, id in self.controls:
            btn.colour = self.get_colour(colours, id)

    def get_colour(self, colours, name):
        colour = self.default[name]
        if name in colours and colours[name] != "[NONE]":
            colour = colours[name]
        return colour
