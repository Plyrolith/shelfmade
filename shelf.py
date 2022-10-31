from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context

from pathlib import Path

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from . import catalogue


########################################################################################
# Update functions
########################################################################################


def update_directory(shelf: Shelf, context: Context):
    """
    Re-scans scripts on any directory change. Saves userprefs.

    Parameters:
        - shelf (Shelf)
        - context (Context)
    """
    if shelf.directory:
        # Make sure the path is normalized
        posix_path = Path(shelf.directory).resolve().as_posix()

        # Set the posix path; this will trigger another update so return
        if shelf.directory != posix_path:
            shelf.directory = posix_path
            return

        # Re-initialize scripts
        shelf.initialize_scripts()

    # Save user preferences
    bpy.ops.wm.save_userpref()


def update_save_userpref(shelf: Shelf, context: Context):
    """
    Save userprefs on update.

    Parameters:
        - shelf (Shelf)
        - context (Context)
    """
    bpy.ops.wm.save_userpref()


########################################################################################
# Script snippet class
########################################################################################


@catalogue.bpy_register
class Script(PropertyGroup):
    """Representation of a single script within a shelf"""

    display_name: StringProperty(name="Name")
    icon: StringProperty(name="Icon", default="NONE")
    is_available: BoolProperty(name="Is Available", default=True)
    name: StringProperty(name="File Name")


########################################################################################
# Shelf class
########################################################################################


@catalogue.bpy_register
class Shelf(PropertyGroup):
    """Single shelf, directory containing scripts to load and display settings"""

    align: BoolProperty(name="Align Buttons")
    columns: IntProperty(name="Columns", default=1, min=1, soft_max=8)
    directory: StringProperty(
        name="Directory",
        subtype="DIR_PATH",
        update=update_directory,
    )

    enabled_view_3d: BoolProperty(name="3D Viewport", default=True)
    enabled_image_editor: BoolProperty(name="Image Editor")
    enabled_uv: BoolProperty(name="UV Editor")
    enabled_compositornodetree: BoolProperty(name="Compositor")
    enabled_texturenodetree: BoolProperty(name="Texture Node Editor")
    enabled_geometrynodetree: BoolProperty(name="Geometry Node Editor")
    enabled_shadernodetree: BoolProperty(name="Shader Editor")
    enabled_sequence_editor: BoolProperty(name="Video Sequencer")
    enabled_clip_editor: BoolProperty(name="Movie Clip Editor")
    enabled_dopesheet: BoolProperty(name="Dope Sheet")
    enabled_timeline: BoolProperty(name="Timeline")
    enabled_fcurves: BoolProperty(name="Graph Editor")
    enabled_drivers: BoolProperty(name="Drivers")
    enabled_nla_editor: BoolProperty(name="Nonlinear Animation")
    enabled_text_editor: BoolProperty(name="Text Editor")
    enabled_spreadsheet: BoolProperty(name="Spreadsheet")

    height: FloatProperty(name="Button Height", default=1.0, min=0.5, soft_max=8.0)
    icon: StringProperty(name="Icon", default="NONE")
    is_available: BoolProperty(name="Is Available")
    name: StringProperty(name="Name")
    scripts: CollectionProperty(type=Script, name="Scripts")
    show_scripts: BoolProperty(name="Show Scripts", default=True)

    def exists(self) -> bool:
        """
        Checks whether this folder exists and sets 'is_available' flag.

        Returns:
            - bool: Whether this folder exists at given location
        """
        if self.directory and Path(self.directory).is_dir():
            self.is_available = True
            return True

        self.is_available = False
        return False

    def initialize_scripts(self):
        """
        Scan the script directory and initiate a script object for each script found.
        """
        if TYPE_CHECKING:
            existing_script: Script
            script: Script

        # Disable all scripts
        [setattr(script, "is_available", False) for script in self.scripts]

        # Check directory
        if not self.exists():
            self.is_available = False
            return

        self.is_available = True

        # Iterate directory and find python scripts
        for script_file in sorted(Path(self.directory).iterdir()):
            if not script_file.suffix == ".py":
                continue

            # Find existing script
            script = None
            for existing_script in self.scripts:
                if existing_script.name == script_file.name:
                    script = existing_script
                    script.is_available = True

            # Create a new script
            if not script:
                script = self.scripts.add()
                script.name = script_file.name
                script.display_name = script_file.stem

    def is_visible(self, context: Context) -> bool:
        """
        Returns:
            - bool: Whether this shelf should be drawn within the given context
        """
        # Always draw in preferences
        area_type = context.area.ui_type
        if area_type == "PREFERENCES":
            return True

        # Check for enabled flag
        attribute_name = f"enabled_{area_type.lower()}"
        if (
            self.is_available
            and hasattr(self, attribute_name)
            and getattr(self, attribute_name)
        ):
            return True

        return False

    def path_is_in_shelf(self, path: str | Path) -> bool:
        """
        Check if given path is located within the shelf directory.

        Parameters:
            - path (str | Path): Path to check

        Returns:
            - bool: Whether the given path is relative to this shelf
        """
        return self.directory in Path(path).resolve().as_posix()

    def script_exists(self, script: int | str) -> bool:
        """
        Checks whether a script exists and sets its 'is_available' flag.

        Parameters:
            - script (int | str): Script index or file name

        Returns:
            - bool: Whether this script exists at expected path or not
        """
        if TYPE_CHECKING:
            script: Script

        script = self.scripts[script]

        if self.script_path(script=script).exists():
            script.is_available = True
            return True

        script.is_available = False
        return False

    def script_path(self, script: int | str) -> Path:
        """
        Generate a path object for given script.

        Parameters:
            - script (int | str): Script index or file name

        Returns:
            - Path
        """
        return Path(self.directory, self.scripts[script].name)
