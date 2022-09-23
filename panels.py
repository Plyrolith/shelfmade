from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context

import bpy
from bpy.types import Panel

from . import catalogue, draw, preferences


########################################################################################
# Panels
########################################################################################


@catalogue.bpy_register
class DirectoryScripts(Panel):
    bl_idname = "SHELFMADE_PT_viewport_directory_scripts"
    bl_category = "Script Shelf"
    bl_label = "Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 20

    @classmethod
    def poll(cls, context: Context) -> bool:
        return bool(preferences.Preferences.this.scripts)

    def draw(self, context: Context):
        draw.directory_scripts(panel=self, context=context)


@catalogue.bpy_register
class LocalScripts(Panel):
    bl_idname = "SHELFMADE_PT_viewport_local_scripts"
    bl_category = "Script Shelf"
    bl_label = "Local Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 30

    @classmethod
    def poll(cls, context: Context) -> bool:
        return any([text.name.endswith(".py") for text in bpy.data.texts])

    def draw(self, context: Context):
        draw.local_scripts(panel=self, context=context)


@catalogue.bpy_register
class Settings(Panel):
    bl_idname = "SHELFMADE_PT_viewport_settings"
    bl_category = "Script Shelf"
    bl_label = "Script Directory"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 10

    def draw(self, context: Context):
        draw.settings(panel=self, context=context)
