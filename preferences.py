from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context, UILayout

import bpy
from bpy.props import BoolProperty, CollectionProperty
from bpy.types import AddonPreferences

from . import catalog, shelf, utils


ENV_VAR = "SHELFMADE_PATH"


@catalog.bpy_register
class Preferences(AddonPreferences):
    """Add-on preferences"""

    bl_idname = __package__ or "shelfmade"

    show_menus: BoolProperty(
        name="Show Menus",
        description="Display shelf menus in UI panels",
    )
    shelves: CollectionProperty(
        type=shelf.Shelf,
        name="Directories",
        description="Shelves, representing directories that contain Python scripts",
    )

    def clean(self):
        """
        Remove all unavailable shelves and scripts.
        """
        if TYPE_CHECKING:
            script: shelf.Script
            shelf: shelf.Shelf

        for i_sh, shelf in reversed(list(enumerate(self.shelves))):
            if not shelf.is_available:
                self.shelves.remove(i_sh)

            for i_sc, script in reversed(list(enumerate(shelf.scripts))):
                if not script.is_available:
                    shelf.scripts.remove(i_sc)

    def create_env_shelves(self):
        """
        Create all shelves defined from env, if they don't exist yet.
        """
        if TYPE_CHECKING:
            shelf: shelf.Shelf

        # Get shelves from environment
        env_paths = utils.env_to_list(ENV_VAR)
        if env_paths:
            for env_path in env_paths:
                # Check if shelf already exists
                if any(
                    utils.same_paths(env_path, shelf.directory)
                    for shelf in self.shelves
                ):
                    continue

                # Create the shelf
                shelf = self.shelves.add()
                shelf.directory = env_path
                shelf.is_locked = True

    def draw(self, context: Context):
        """
        Draw add-on the preferences panel. Displays an overview of all shelves with all
        their respective properties and operators laid out.

        Args:
            context (Context)
        """
        if TYPE_CHECKING:
            layout: UILayout
            shelf: shelf.Shelf

        # Add shelf button
        layout = self.layout
        col_shelves = layout.column(align=True)
        col_shelves.row(align=True).operator(
            operator="shelfmade.add_shelf",
            icon="ADD",
        )

        if not self.shelves:
            return

        # Draw all shelves
        box_shelves = col_shelves.box()
        box_shelves.separator()
        for i, shelf in enumerate(self.shelves):
            row_shelf = box_shelves.row()

            # Icon
            row_name = row_shelf.row(align=True)
            row_name.enabled = not shelf.is_locked
            row_name.operator(
                operator="shelfmade.set_shelf_icon",
                text="",
                icon="BLANK1" if shelf.icon == "NONE" else shelf.icon,
            ).index = i

            # Name
            row_name.prop(shelf, "name", text="")

            # Visibility
            row_vis = row_shelf.row()
            row_vis.enabled = not shelf.is_locked
            row_vis.operator(
                operator="shelfmade.edit_shelf_visibility",
                text="",
                icon="VIS_SEL_11",
            ).index = i

            # Path
            split_path = row_shelf.split(factor=0.8, align=True)
            split_path.enabled = not shelf.is_locked
            split_path.prop(shelf, "directory", text="")
            split_path.prop(shelf, "use_json", text="JSON", toggle=True)

            # Lock
            row_lock = row_shelf.row()
            if shelf.use_json:
                row_lock.operator(
                    "shelfmade.edit_shelf_lock",
                    text="",
                    icon="LOCKED" if shelf.is_locked else "UNLOCKED",
                ).index = i
            else:
                row_lock.label(text="", icon="BLANK1")

            # Move
            row_move = row_shelf.row(align=True)
            row_up = row_move.row(align=True)
            if i == 0:
                row_up.enabled = False
            up = row_up.operator(
                operator="shelfmade.move_shelf",
                text="",
                icon="TRIA_UP",
            )
            up.direction = "UP"
            up.index = i

            row_down = row_move.row(align=True)
            if i == len(self.shelves) - 1:
                row_down.enabled = False
            down = row_down.operator(
                operator="shelfmade.move_shelf",
                text="",
                icon="TRIA_DOWN",
            )
            down.direction = "DOWN"
            down.index = i

            # Remove
            row_shelf.operator(
                operator="shelfmade.remove_shelf",
                text="",
                icon="X",
            ).index = i

    def initialize_shelves(self):
        """
        Scan the script directories and initiate a script object for each script found.
        """
        if TYPE_CHECKING:
            shelf: shelf.Shelf

        # Scan all shelf directories
        for shelf in self.shelves:
            shelf.initialize()

    @staticmethod
    def register():
        """
        Initialize shelves & remove nonexistent shelves & scripts.
        """
        prefs = Preferences.this()
        prefs.create_env_shelves()
        prefs.initialize_shelves()
        prefs.clean()

    @staticmethod
    def this() -> Preferences:
        """
        Preference class instance pointer for shortcuts.

        Returns:
            Preferences: bpy instance
        """
        prefs = bpy.context.preferences.addons[__package__ or "shelfmade"].preferences
        if not prefs:
            raise ValueError("Add-on Preferences not found.")
        return prefs  # type: ignore
