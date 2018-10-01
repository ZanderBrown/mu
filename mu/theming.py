import re
from PyQt5.QtGui import QColor


class Theme:
    def __init__(self):
        self.source = ""
        self.vars = {}

    def load_source(self, path):
        """
        Load source into the theme
        """
        with open(path, "r") as f:
            self.source += "\n" + f.read()

    def __getitem__(self, key):
        """
        Get an assigned QColor by name
        """
        return self.vars[key]

    def __setitem__(self, key, value):
        """
        Set the QColor value for key
        """
        # We only expect QColors
        if not isinstance(value, QColor):
            raise TypeError("Expected a QColor")
        self.vars[key] = value

    def __str__(self):
        """
        Generate the CSS string for this theme
        """
        # Find all placeholders using self._repl to get
        # their values
        return re.sub("%:(.*):%", self._repl, self.source)

    def _repl(self, m):
        """
        Return the CSS value of the name matched in m
        """
        return self.vars[m.group(1)].name()
