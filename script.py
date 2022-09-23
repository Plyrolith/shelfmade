from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Text

from pathlib import Path

import bpy
from bpy.props import StringProperty
from bpy.types import PropertyGroup

from . import catalogue, utils

########################################################################################
# Script snippet class
########################################################################################


@catalogue.bpy_register
class Script(PropertyGroup):
    """Representation of a single script within the scripts directory"""

    name: StringProperty(name="Name")
    filepath: StringProperty(name="File Path", subtype="FILE_PATH")

    def exists(self) -> bool:
        """
        Returns:
            - bool: Whether this script exists at expected path or not
        """
        return Path(self.filepath).exists()

    def run(self):
        """
        Run this script.
        """
        exec(compile(open(self.filepath).read(), self.filepath, "exec"))

    def load(self) -> Text:
        """
        Load this script as local text file. Create a new datablock if needed.

        Returns:
            - Text: Blender text datablock
        """
        # Try to find existing text
        texts = bpy.data.texts[:]
        for text in texts:
            if utils.same_paths([self.filepath, text.filepath]):
                return text

        # Open text via operator and find/return it
        bpy.ops.text.open(filepath=self.filepath)
        for text in bpy.data.texts:
            if text not in texts:
                return text
