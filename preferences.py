from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context, UILayout

import bpy
from bpy.props import BoolProperty, CollectionProperty
from bpy.types import AddonPreferences

from . import catalog, shelf


@catalog.bpy_register
class Preferences(AddonPreferences):
    """Add-on preferences"""

    bl_idname = __package__ or "shelfmade"

    is_locked: BoolProperty(name="(Un)Lock Shelves", update=shelf.update_save_userpref)
    shelves: CollectionProperty(type=shelf.Shelf, name="Directories")

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
            row_name.operator(
                operator="shelfmade.set_shelf_icon",
                text="",
                icon="BLANK1" if shelf.icon == "NONE" else shelf.icon,
            ).index = i

            # Name
            row_name.prop(shelf, "name", text="")

            # Visibility
            row_shelf.operator(
                operator="shelfmade.edit_shelf_visibility",
                text="",
                icon="VIS_SEL_11",
            ).index = i

            # Path
            split_path = row_shelf.split(factor=0.8, align=True)
            split_path.prop(shelf, "directory", text="")
            split_path.prop(shelf, "use_json_file", text="JSON", toggle=True)

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
        Preferences.this().initialize_shelves()
        Preferences.this().clean()

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
