from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context
    from .script import Script

import bpy
from bpy.props import IntProperty
from bpy.types import Operator

from . import catalogue, preferences, utils


########################################################################################
# Operators
########################################################################################


@catalogue.bpy_register
class SHELFMADE_OT_EditScript(Operator):
    """Edit this Python script file in the text editor"""

    bl_idname = "wm.shelfmade_edit_script"
    bl_label = "Edit Shelf Script"
    bl_options = {"INTERNAL", "UNDO"}

    index: IntProperty()

    def execute(self, context: Context):
        if TYPE_CHECKING:
            script: Script

        prefs = preferences.Preferences.this

        # Check the script
        script = prefs.scripts[self.index]
        if not script.exists():
            print(f"Script file {script.name} not found")
            prefs.initialize_scripts()
            return {"CANCELLED"}

        # Load the script
        text = script.load()

        # Ensure text editor
        area = utils.find_or_create_area(
            context=context,
            type="TEXT_EDITOR",
            direction="VERTICAL",
            factor=0.5,
        )

        # Open script in text editor
        area.spaces[0].text = text

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_ReloadScripts(Operator):
    """Re-scan the scripts directory and build script list"""

    bl_idname = "wm.shelfmade_reload_scripts"
    bl_label = "Reload Scripts"
    bl_options = {"INTERNAL", "UNDO"}

    @classmethod
    def poll(self, context: Context) -> bool:
        return bool(preferences.Preferences.this.script_directory)

    def execute(self, context: Context):
        preferences.Preferences.this.initialize_scripts()
        utils.ui_redraw(context=context)

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_RunScript(Operator):
    """Execute this Python script file"""

    bl_idname = "wm.shelfmade_run_script"
    bl_label = "Run Shelf Script"
    bl_options = {"INTERNAL", "UNDO"}

    index: IntProperty()

    def execute(self, context: Context):
        if TYPE_CHECKING:
            script: Script

        prefs = preferences.Preferences.this

        # Check the script
        script = prefs.scripts[self.index]
        if not script.exists():
            print(f"Script file {script.name} not found")
            prefs.initialize_scripts()
            return {"CANCELLED"}

        script.run()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_RunText(Operator):
    """Execute this local text datablock"""

    bl_idname = "wm.shelfmade_run_text"
    bl_label = "Run Text Datablock"
    bl_options = {"INTERNAL", "UNDO"}

    index: IntProperty()

    def execute(self, context: Context):
        # Run the local script using the basic operator
        with context.temp_override(edit_text=bpy.data.texts[self.index]):
            bpy.ops.text.run_script()

        return {"FINISHED"}
