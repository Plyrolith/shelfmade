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
    EnumProperty,
    FloatProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from . import catalog, utils


@catalog.bpy_register
class Author(PropertyGroup):
    """User with permissions to edit a shelf"""

    def save(self, context: Context | None = None):
        """
        Save to JSON or save userprefs, based on properties.

        Args:
            context (Context | None)
        """
        self.get_shelf().save(context)

    name: StringProperty(
        name="Username",
        description="OS username for a user with edit permissions",
        update=save,
    )

    def get_shelf(self) -> Shelf:
        """
        Return this author's shelf object.

        Returns:
            Shelf
        """
        if TYPE_CHECKING:
            shelf: Shelf

        shelf = self.rna_ancestors()[-1]  # type: ignore
        return shelf


@catalog.bpy_register
class Script(PropertyGroup):
    """Representation of a single script within a shelf"""

    def save(self, context: Context | None = None):
        """
        Save to JSON or save userprefs, based on properties.

        Args:
            context (Context | None)
        """
        self.get_shelf().save(context)

    display_name: StringProperty(
        name="Name",
        description="The name displayed in the UI",
        update=save,
    )
    height: FloatProperty(
        name="Button Height",
        description="Height of this script's button row",
        default=1.0,
        min=0.5,
        soft_max=8.0,
        update=save,
    )
    icon: EnumProperty(
        items=utils.enum_icons,  # type: ignore
        name="Icon",
        description="The icon representing this script",
        update=save,
    )
    is_available: BoolProperty(
        name="Is Available",
        description="Whether this script is accessible or not",
        default=True,
    )
    is_focused: BoolProperty(
        name="Is Focused",
        description="This script is focused for editing by an operator",
    )
    name: StringProperty(
        name="File Name",
        description="File name of the Python script within the shelf directory",
    )
    spacing: EnumProperty(
        items=(
            ("ALIGN", "Merge", "Merge with previous script"),
            ("NONE", "Default", "Default spacing"),
            ("SPACE", "Gap", "Leave a gap after this script"),
            ("LINE", "Line", "Separate this script with a line from the next one"),
        ),
        name="Spacing",
        description="How this script is separated from the previous script's button",
        default="NONE",
        update=save,
    )
    use_attach: BoolProperty(
        name="Attach",
        description="Attach this script's button to the previous row",
        update=save,
    )

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


@catalog.bpy_register
class Shelf(PropertyGroup):
    """Single shelf, directory containing scripts to load and display settings"""

    def save(self, context: Context | None = None):
        """
        Save to JSON or save userprefs, based on properties.

        Args:
            context (Context | None)
        """
        if not context:
            context = bpy.context

        if not self.is_available or self.is_locked:
            return

        elif self.use_json:
            self.save_json()

        elif hasattr(context, "view_layer"):
            bpy.ops.wm.save_userpref()

    def update_directory(self, context: Context):
        """
        Re-scans scripts on any directory change. Saves userprefs.

        Args:
            context (Context)
        """
        if self.directory:
            # Make sure the path is normalized
            posix_path = Path(self.directory).resolve().as_posix()

            # Set the posix path; this will trigger another update so return
            if self.directory != posix_path:
                self.directory = posix_path
                return

            # Re-initialize scripts
            self.initialize()

        # Save JSON or user preferences
        self.save(context)

    authors: CollectionProperty(
        type=Author,
        name="Authors",
        description="OS users with unlock and edit permissions",
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
        update=save,
    )
    enabled_image_editor: BoolProperty(
        name="Image Editor",
        description="Whether to show this shelf in the image editor",
        update=save,
    )
    enabled_uv: BoolProperty(
        name="UV Editor",
        description="Whether to show this shelf in the UV editor",
        update=save,
    )
    enabled_compositornodetree: BoolProperty(
        name="Compositor",
        description="Whether to show this shelf in the compositor",
        update=save,
    )
    enabled_texturenodetree: BoolProperty(
        name="Texture Node Editor",
        description="Whether to show this shelf in the texture node editor",
        update=save,
    )
    enabled_geometrynodetree: BoolProperty(
        name="Geometry Node Editor",
        description="Whether to show this shelf in the geomoetry node editor",
        update=save,
    )
    enabled_shadernodetree: BoolProperty(
        name="Shader Editor",
        description="Whether to show this shelf in the shader editor",
        update=save,
    )
    enabled_sequence_editor: BoolProperty(
        name="Video Sequencer",
        description="Whether to show this shelf in the sequence editor",
        update=save,
    )
    enabled_clip_editor: BoolProperty(
        name="Movie Clip Editor",
        description="Whether to show this shelf in the video clip editor",
        update=save,
    )
    enabled_dopesheet: BoolProperty(
        name="Dope Sheet",
        description="Whether to show this shelf in the dope sheet",
        update=save,
    )
    enabled_timeline: BoolProperty(
        name="Timeline",
        description="Whether to show this shelf in the timeline",
        update=save,
    )
    enabled_fcurves: BoolProperty(
        name="Graph Editor",
        description="Whether to show this shelf in the graph editor",
        update=save,
    )
    enabled_drivers: BoolProperty(
        name="Drivers",
        description="Whether to show this shelf in the drivers editor",
        update=save,
    )
    enabled_nla_editor: BoolProperty(
        name="Nonlinear Animation",
        description="Whether to show this shelf in the NLA editor",
        update=save,
    )
    enabled_text_editor: BoolProperty(
        name="Text Editor",
        description="Whether to show this shelf in the text editor",
        update=save,
    )
    enabled_spreadsheet: BoolProperty(
        name="Spreadsheet",
        description="Whether to show this shelf in the spreadsheet",
        update=save,
    )

    icon: EnumProperty(
        items=utils.enum_icons,  # type: ignore
        name="Icon",
        description="The icon representing this shelf",
        update=save,
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
        update=save,
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
        update=save,
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

        # Lock if user is not in authors list
        if not self.is_locked:
            self.is_locked = not self.is_unlockable()

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
                    script.is_focused = False

            # Create a new script
            if not script:
                script = self.scripts.add()
                script.name = script_file.name
                script.display_name = script_file.stem
                has_new_scripts = True

        # Save new scripts
        if has_new_scripts:
            self.save()

    def is_unlockable(self) -> bool:
        """
        Check if the current user has permissions to unlock this shelf.

        Returns:
            bool: Whether the shelf can be unlocked
        """
        if TYPE_CHECKING:
            author: Author

        if not self.authors:
            return True

        for author in self.authors:
            if author.name == utils.get_user():
                return True

        return False

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

    def load_json(self) -> dict[str, bool | int | float | str | list | dict] | None:
        """
        Load this shelve's JSON file and parse data.

        Returns:
            dict | None: JSON dict if file exists
        """
        file_name = self.json_filename
        if not file_name:
            file_name = ".shelfmade"

        json_path = Path(self.directory, file_name).with_suffix(".json")
        if not json_path.is_file():
            return

        # Lock to avoid save trigger
        exception = None
        shelf_dict = {}
        is_locked = self.is_locked
        self.is_locked = True

        try:
            with open(json_path, "r") as file:
                shelf_dict = json.load(file)
                utils.dict_to_property_group(self, shelf_dict)

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
            "use_json",
        ):
            shelf_dict.pop(shelf_prop, None)
        for script_dict in shelf_dict.get("scripts", []):  # type: ignore
            for script_prop in ("is_available", "is_focused"):
                script_dict.pop(script_prop, None)

        return shelf_dict
