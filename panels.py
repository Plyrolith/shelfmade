from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context

import bpy
from bpy.types import Panel

from . import catalogue, draw, preferences


########################################################################################
# Base panels
########################################################################################


@catalogue.bpy_register
class LocalShelf(Panel):
    bl_idname = "SHELFMADE_PT_viewport_local_shelf"
    bl_category = "Shelf Made"
    bl_label = "Local Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 100

    @classmethod
    def poll(cls, context: Context) -> bool:
        return any([text.name.endswith(".py") for text in bpy.data.texts])

    def draw(self, context: Context):
        draw.local_scripts(panel=self, context=context)


# Not registered, serves as base
class Shelves(Panel):
    bl_category = "Shelf Made"
    bl_label = "Shelves"
    bl_region_type = "UI"
    bl_options = {"HEADER_LAYOUT_EXPAND"}
    bl_order = 110

    @classmethod
    def poll(cls, context: Context) -> bool:
        shelves = preferences.Preferences.this().shelves
        return not shelves or any(
            [
                getattr(shelf, f"enabled_{context.area.ui_type.lower()}")
                for shelf in shelves
            ]
        )

    def draw_header(self, context: Context):
        prefs = preferences.Preferences.this()
        if not prefs.shelves:
            return

        row_header = self.layout.row(align=True)
        row_header.alignment = "RIGHT"
        row_header.operator(operator="shelfmade.add_shelf", text="", icon="ADD")
        row_header.operator(
            operator="shelfmade.reload",
            text="",
            icon="FILE_REFRESH",
        )

        row_header.prop(
            data=prefs,
            property="is_locked",
            text="",
            icon="LOCKED" if prefs.is_locked else "UNLOCKED",
        )

    def draw(self, context: Context):
        draw.shelf_scripts(panel=self, context=context)


########################################################################################
# Shelf panels
########################################################################################


@catalogue.bpy_register
class ClipEditorShelves(Shelves):
    bl_idname = "SHELFMADE_PT_clip_editor_shelves"
    bl_space_type = "CLIP_EDITOR"


@catalogue.bpy_register
class DopesheetEditorShelves(Shelves):
    bl_idname = "SHELFMADE_PT_dopesheet_editor_shelves"
    bl_space_type = "DOPESHEET_EDITOR"


@catalogue.bpy_register
class FileBrowserShelves(Shelves):
    bl_idname = "SHELFMADE_PT_file_browser_shelves"
    bl_space_type = "FILE_BROWSER"


@catalogue.bpy_register
class GraphEditorShelves(Shelves):
    bl_idname = "SHELFMADE_PT_graph_editor_shelves"
    bl_space_type = "GRAPH_EDITOR"


@catalogue.bpy_register
class ImageEditorShelves(Shelves):
    bl_idname = "SHELFMADE_PT_image_editor_shelves"
    bl_space_type = "IMAGE_EDITOR"


@catalogue.bpy_register
class NlaEditorShelves(Shelves):
    bl_idname = "SHELFMADE_PT_nla_editor_shelves"
    bl_space_type = "NLA_EDITOR"


@catalogue.bpy_register
class NodeEditorShelves(Shelves):
    bl_idname = "SHELFMADE_PT_node_editor_shelves"
    bl_space_type = "NODE_EDITOR"


@catalogue.bpy_register
class SequenceEditorShelves(Shelves):
    bl_idname = "SHELFMADE_PT_sequence_editor_shelves"
    bl_space_type = "SEQUENCE_EDITOR"


@catalogue.bpy_register
class SpreadsheetShelves(Shelves):
    bl_idname = "SHELFMADE_PT_spreadsheet_shelves"
    bl_space_type = "SPREADSHEET"


@catalogue.bpy_register
class TextEditorShelves(Shelves):
    bl_idname = "SHELFMADE_PT_text_editor_shelves"
    bl_space_type = "TEXT_EDITOR"


@catalogue.bpy_register
class ViewportShelves(Shelves):
    bl_idname = "SHELFMADE_PT_view_3d_shelves"
    bl_space_type = "VIEW_3D"
