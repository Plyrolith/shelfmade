from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context

import bpy
from bpy.types import Panel

from . import catalog, draw, preferences


@catalog.bpy_register
class LocalShelf(Panel):
    """Displays one operator for each Python script in the current blend file"""

    bl_idname = "SHELFMADE_PT_viewport_local_shelf"
    bl_category = "Shelf Made"
    bl_label = "Local Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 100
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        Draw this panel only if any Python script ending in '.py' exists within the
        loaded blend file.

        Args:
            context (Context)

        Returns:
            bool: Whether this panel is drawn or not
        """
        return any([text.name.endswith(".py") for text in bpy.data.texts])

    def draw(self, context: Context):
        draw.local_scripts(self, context)


# Not registered, serves as base
class Shelves(Panel):
    """Displays all visible shelves; inherited by its registered area equivalents"""

    bl_category = "Shelf Made"
    bl_label = "Shelves"
    bl_region_type = "UI"
    bl_options = {"HEADER_LAYOUT_EXPAND"}
    bl_order = 110

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        Draw this panel only if any existing shelf is visible. If there are no shelves,
        the panels drawn within all allowed areas (displaying only the 'Add Shelf'
        operator).

        Args:
            context (Context)

        Returns:
            bool: Whether this panel is drawn or not
        """
        shelves = preferences.Preferences.this().shelves
        return any([shelf.is_visible(context) for shelf in shelves]) or (
            not shelves and context.area.ui_type in draw.AREA_TYPES.keys()
        )

    def draw_header(self, context: Context):
        """
        Draw the header row if this panel.

        Args:
            context (Context)
        """
        prefs = preferences.Preferences.this()
        if not prefs.shelves:
            return

        row_header = self.layout.row(align=True)
        row_header.alignment = "RIGHT"
        row_header.operator("shelfmade.add_shelf", text="", icon="ADD")
        row_header.operator(
            operator="shelfmade.reload",
            text="",
            icon="FILE_REFRESH",
        )

        row_header.prop(
            prefs,
            "show_menus",
            text="",
            icon="KEY_MENU_FILLED" if prefs.show_menus else "KEY_MENU",
            toggle=True,
        )

    def draw(self, context: Context):
        """
        Draw the collapsable main body of this panel.

        Args:
            context (Context)
        """
        draw.shelf_scripts(self, context)


# (Inheriting) shelf panels


@catalog.bpy_register
class ClipEditorShelves(Shelves):
    """Shelf panel for the Clip Editor"""

    bl_idname = "SHELFMADE_PT_clip_editor_shelves"
    bl_space_type = "CLIP_EDITOR"


@catalog.bpy_register
class DopesheetEditorShelves(Shelves):
    """Shelf panel for the Dopesheet Editor"""

    bl_idname = "SHELFMADE_PT_dopesheet_editor_shelves"
    bl_space_type = "DOPESHEET_EDITOR"


@catalog.bpy_register
class FileBrowserShelves(Shelves):
    """Shelf panel for the File Browser"""

    bl_idname = "SHELFMADE_PT_file_browser_shelves"
    bl_space_type = "FILE_BROWSER"


@catalog.bpy_register
class GraphEditorShelves(Shelves):
    """Shelf panel for the Graph Editor"""

    bl_idname = "SHELFMADE_PT_graph_editor_shelves"
    bl_space_type = "GRAPH_EDITOR"


@catalog.bpy_register
class ImageEditorShelves(Shelves):
    """Shelf panel for the Image Editor"""

    bl_idname = "SHELFMADE_PT_image_editor_shelves"
    bl_space_type = "IMAGE_EDITOR"


@catalog.bpy_register
class NlaEditorShelves(Shelves):
    """Shelf panel for the NLA Editor"""

    bl_idname = "SHELFMADE_PT_nla_editor_shelves"
    bl_space_type = "NLA_EDITOR"


@catalog.bpy_register
class NodeEditorShelves(Shelves):
    """Shelf panel for the Node Editor"""

    bl_idname = "SHELFMADE_PT_node_editor_shelves"
    bl_space_type = "NODE_EDITOR"


@catalog.bpy_register
class SequenceEditorShelves(Shelves):
    """Shelf panel for the Sequence Editor"""

    bl_idname = "SHELFMADE_PT_sequence_editor_shelves"
    bl_space_type = "SEQUENCE_EDITOR"


@catalog.bpy_register
class SpreadsheetShelves(Shelves):
    """Shelf panel for the Spreadsheet Editor"""

    bl_idname = "SHELFMADE_PT_spreadsheet_shelves"
    bl_space_type = "SPREADSHEET"


@catalog.bpy_register
class TextEditorShelves(Shelves):
    """Shelf panel for the Text Editor"""

    bl_idname = "SHELFMADE_PT_text_editor_shelves"
    bl_space_type = "TEXT_EDITOR"

    @staticmethod
    def register():
        """
        Add the shelf menu to text editor.
        """
        bpy.types.TEXT_HT_header.append(draw.text_editor_shelf_menu)

    @staticmethod
    def unregister():
        """
        Remove the text editor draw function.
        """
        bpy.types.TEXT_HT_header.remove(draw.text_editor_shelf_menu)


@catalog.bpy_register
class ViewportShelves(Shelves):
    """Shelf panel for the 3D Viewport"""

    bl_idname = "SHELFMADE_PT_view_3d_shelves"
    bl_space_type = "VIEW_3D"
