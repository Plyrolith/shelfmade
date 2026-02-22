from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike
    from bpy.types import Context

import json
from pathlib import Path

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from . import catalog, utils

# Update functions


def update_directory(shelf: Shelf, context: Context):
    """
    Re-scans scripts on any directory change. Saves userprefs.

    Args:
        shelf (Shelf)
        context (Context)
    """
    if shelf.directory:
        # Make sure the path is normalized
        posix_path = Path(shelf.directory).resolve().as_posix()

        # Set the posix path; this will trigger another update so return
        if shelf.directory != posix_path:
            shelf.directory = posix_path
            return

        # Re-initialize scripts
        shelf.initialize()

    # Save user preferences
    bpy.ops.wm.save_userpref()


def update_save_userpref(shelf: Shelf, context: Context):
    """
    Save userprefs on update.

    Args:
        shelf (Shelf)
        context (Context)
    """
    bpy.ops.wm.save_userpref()


def update_save_json(self: Script | Shelf, context: Context):
    """
    Save to JSON on update, if flag is set.

    Args:
        shelf (Shelf)
        context (Context)
    """
    self.save_json()


# Script snippet class


@catalog.bpy_register
class Script(PropertyGroup):
    """Representation of a single script within a shelf"""

    display_name: StringProperty(
        name="Name",
        description="The name displayed in the UI",
        update=update_save_json,
    )
    icon: StringProperty(
        name="Icon",
        default="NONE",
        description="The icon representing this script",
        update=update_save_json,
    )
    is_available: BoolProperty(
        name="Is Available",
        description="Whether this script is accessible or not",
        default=True,
    )
    name: StringProperty(
        name="File Name",
        description="File name of the Python script within the shelf directory",
    )

    def exists(self) -> bool:
        """
        Checks whether this script exists and sets its 'is_available' flag.


        Returns:
            bool: Whether this script exists at expected path or not
        """
        if self.get_path().exists():
            self.is_available = True
            return True

        self.is_available = False
        return False

    def get_path(self) -> Path:
        """
        Generate a path object for this script.

        Returns:
            Path
        """
        return Path(self.get_shelf().directory, self.name)

    def get_shelf(self) -> Shelf:
        """
        Return this script's shelf object.

        Returns:
            Shelf
        """
        if TYPE_CHECKING:
            shelf: Shelf

        shelf = self.rna_ancestors()[-1]  # type: ignore
        return shelf

    def save_json(self, force: bool = False) -> Path | None:
        """
        Save this script's shelf to its JSON file, if conditions allow it.

        Args:
            force (bool): Save even when conditions aren't met.

        Returns:
            Path | None: Absolute path to the saved JSON file
        """
        return self.get_shelf().save_json(force)


# Shelf class


@catalog.bpy_register
class Shelf(PropertyGroup):
    """Single shelf, directory containing scripts to load and display settings"""

    align: BoolProperty(
        name="Align Buttons",
        description="Align all buttons and remove all padding for the whole shelf",
        update=update_save_json,
    )
    columns: IntProperty(
        name="Columns",
        description="Split the shelf's buttons into this number of columns",
        default=1,
        min=1,
        soft_max=8,
        update=update_save_json,
    )
    directory: StringProperty(
        name="Directory",
        description="The directory for this shelf, containing Python scripts",
        subtype="DIR_PATH",
        update=update_directory,
    )

    enabled_view_3d: BoolProperty(
        name="3D Viewport",
        description="Whether to show this shelf in the 3D viewport",
        default=True,
        update=update_save_json,
    )
    enabled_image_editor: BoolProperty(
        name="Image Editor",
        description="Whether to show this shelf in the image editor",
        update=update_save_json,
    )
    enabled_uv: BoolProperty(
        name="UV Editor",
        description="Whether to show this shelf in the UV editor",
        update=update_save_json,
    )
    enabled_compositornodetree: BoolProperty(
        name="Compositor",
        description="Whether to show this shelf in the compositor",
        update=update_save_json,
    )
    enabled_texturenodetree: BoolProperty(
        name="Texture Node Editor",
        description="Whether to show this shelf in the texture node editor",
        update=update_save_json,
    )
    enabled_geometrynodetree: BoolProperty(
        name="Geometry Node Editor",
        description="Whether to show this shelf in the geomoetry node editor",
        update=update_save_json,
    )
    enabled_shadernodetree: BoolProperty(
        name="Shader Editor",
        description="Whether to show this shelf in the shader editor",
        update=update_save_json,
    )
    enabled_sequence_editor: BoolProperty(
        name="Video Sequencer",
        description="Whether to show this shelf in the sequence editor",
        update=update_save_json,
    )
    enabled_clip_editor: BoolProperty(
        name="Movie Clip Editor",
        description="Whether to show this shelf in the video clip editor",
        update=update_save_json,
    )
    enabled_dopesheet: BoolProperty(
        name="Dope Sheet",
        description="Whether to show this shelf in the dope sheet",
        update=update_save_json,
    )
    enabled_timeline: BoolProperty(
        name="Timeline",
        description="Whether to show this shelf in the timeline",
        update=update_save_json,
    )
    enabled_fcurves: BoolProperty(
        name="Graph Editor",
        description="Whether to show this shelf in the graph editor",
        update=update_save_json,
    )
    enabled_drivers: BoolProperty(
        name="Drivers",
        description="Whether to show this shelf in the drivers editor",
        update=update_save_json,
    )
    enabled_nla_editor: BoolProperty(
        name="Nonlinear Animation",
        description="Whether to show this shelf in the NLA editor",
        update=update_save_json,
    )
    enabled_text_editor: BoolProperty(
        name="Text Editor",
        description="Whether to show this shelf in the text editor",
        update=update_save_json,
    )
    enabled_spreadsheet: BoolProperty(
        name="Spreadsheet",
        description="Whether to show this shelf in the spreadsheet",
        update=update_save_json,
    )

    height: FloatProperty(
        name="Button Height",
        description="Global height of all script buttons",
        default=1.0,
        min=0.5,
        soft_max=8.0,
        update=update_save_json,
    )
    icon: StringProperty(
        name="Icon",
        default="NONE",
        description="The icon representing this shelf",
        update=update_save_json,
    )
    is_available: BoolProperty(
        name="Is Available",
        description="Whether the shelf's directory is accessible or not",
    )
    is_locked: BoolProperty(
        name="Locked",
        description="Whether this shelf is locked, preventing any changes",
    )
    json_filename: StringProperty(
        name="JSON Filename",
        description="Name of the JSON file where this shelf's data should be stored in",
        default=".shelfmade",
    )
    name: StringProperty(
        name="Name",
        description="Name of this shelf, will be used for the UI",
        update=update_save_json,
    )
    scripts: CollectionProperty(
        type=Script,
        name="Scripts",
        description="This shelf's script objects",
    )
    show_scripts: BoolProperty(
        name="Show Scripts",
        description="Expand this shelf",
        default=True,
    )
    use_json: BoolProperty(
        name="Save to JSON",
        description="Save this shelf to a JSON file or in Blender's preferences only",
        default=True,
        update=update_save_json,
    )

    def exists(self) -> bool:
        """
        Checks whether this folder exists and sets 'is_available' flag.

        Returns:
            bool: Whether this folder exists at given location
        """
        if self.directory and Path(self.directory).is_dir():
            self.is_available = True
            return True

        self.is_available = False
        return False

    def initialize(self):
        """
        Scan the script directory and initiate a script object for each script found.
        """
        if TYPE_CHECKING:
            existing_script: Script
            script: Script | None

        # Disable all scripts
        [setattr(script, "is_available", False) for script in self.scripts]

        # Check directory
        if not self.exists():
            self.is_available = False
            return

        self.is_available = True

        # Read from JSON config
        if self.use_json:
            self.load_json()

        # Set name
        if not self.name:
            self.name = Path(self.directory).name

        # Iterate directory and find python scripts
        has_new_scripts = False
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
                has_new_scripts = True

        # Save new sscripts to JSON
        if has_new_scripts:
            self.save_json()

    def is_visible(self, context: Context):
        """
        Returns:
            bool: Whether this shelf should be drawn within the given context
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

    def load_json(self) -> dict[str, bool | int | float | str | list | dict]:
        """
        Load this shelve's JSON file and parse data.

        Returns:
            dict
        """
        if TYPE_CHECKING:
            script: Script
            shelf_dict: dict[str, bool | int | float | str | list | dict]
            script_dict: dict[str, bool | int | float | str]

        file_name = self.json_filename
        if not file_name:
            file_name = ".shelfmade"

        json_path = Path(self.directory, file_name).with_suffix(".json")

        # Lock to avoid save trigger
        exception = None
        is_locked = self.is_locked
        self.is_locked = True

        with open(json_path, "r") as file:
            shelf_dict = json.load(file)
            try:
                for shelf_key, shelf_value in shelf_dict.items():
                    if shelf_key == "scripts":
                        for script_dict in shelf_value:  # type: ignore
                            # Find script by file name
                            script_name = script_dict.pop("name")
                            script = self.scripts.get(script_name)

                            # Create a new one
                            if not script:
                                script = self.scripts.add()
                                script.name = script_name

                            # Set script props
                            for script_key, script_value in script_dict.items():
                                setattr(script, script_key, script_value)
                    else:
                        # Set shelf props
                        setattr(self, shelf_key, shelf_value)

            except Exception as e:
                exception = e

        # Restore previous locked state
        self.is_locked = is_locked
        if exception:
            raise exception

        return shelf_dict

    def path_is_in_shelf(self, path: str | PathLike) -> bool:
        """
        Check if given path is located within the shelf directory.

        Args:
            path (str | PathLike): Path to check

        Returns:
            bool: Whether the given path is relative to this shelf
        """
        return self.directory in Path(path).resolve().as_posix()

    def save_json(self, force: bool = False) -> Path | None:
        """
        Save this shelf to its JSON file, if conditions allow it.

        Args:
            force (bool): Save even when conditions aren't met.

        Returns:
            Path | None: Absolute path to the saved JSON file
        """
        if not force and (not self.is_available or not self.use_json or self.is_locked):
            return

        file_name = self.json_filename
        if not file_name:
            file_name = ".shelfmade"

        json_path = Path(self.directory, file_name).with_suffix(".json")
        shelf_dict = self.to_dict()

        with open(json_path, "w") as file:
            json.dump(shelf_dict, file, indent=2)

        return json_path

    def to_dict(self) -> dict[str, bool | int | float | str | list | dict]:
        """
        Convert this shelf into a dictionary object.

        Returns:
            dict[str, bool | int | float | str]
        """
        if TYPE_CHECKING:
            script_dict: dict[str, bool | str]

        shelf_dict = utils.annotations_to_dict(self)
        for shelf_prop in (
            "directory",
            "is_available",
            "is_locked",
            "json_filename",
            "show_scripts",
            "use_json_file",
        ):
            shelf_dict.pop(shelf_prop, None)
        for script_dict in shelf_dict.get("scripts", []):  # type: ignore
            for script_prop in ("is_available",):
                script_dict.pop(script_prop, None)

        return shelf_dict
