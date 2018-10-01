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
            return self.dlg.selectedColor()
        return self._colour


class ColourWidget(QWidget):
    """
    Configure colours
    """

    def __init__(self, parent):
        super().__init__(parent)
        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)
        # Foreground
        col = QColor(255, 0, 0)
        self.foreground = ColourButton(self, col)
        layout.addWidget(self.foreground, 0, 0, Qt.AlignLeft)
        lbl = QLabel(_("Foreground"))
        layout.addWidget(lbl, 0, 1, Qt.AlignLeft)
        # Background
        col = QColor(0, 255, 0)
        self.background = ColourButton(self, col)
        layout.addWidget(self.background, 1, 0, Qt.AlignLeft)
        lbl = QLabel(_("Background"))
        layout.addWidget(lbl, 1, 1, Qt.AlignLeft)
        # Border
        col = QColor(0, 0, 255)
        self.border = ColourButton(self, col)
        layout.addWidget(self.border, 2, 0, Qt.AlignLeft)
        lbl = QLabel(_("Border"))
        layout.addWidget(lbl, 2, 1, Qt.AlignLeft)
