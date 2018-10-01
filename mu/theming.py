"""
Generate stylesheet

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
