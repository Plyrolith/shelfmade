from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Tuple
    from bpy.types import Context, Event
    from . import shelf

from pathlib import Path

import bpy
from bpy.props import EnumProperty, IntProperty, StringProperty
from bpy.types import Operator
from bpy_extras import io_utils

from . import catalogue, draw, preferences, utils


########################################################################################
# Enumerator
########################################################################################


def enum_icons(
    operator: SHELFMADE_OT_SetScriptIcon,
    context: Context,
) -> List[Tuple[str, str, str, str, int]]:
    """
    Return the enumerator containing all availble Blender icons.
    """
    enum_icons = (
        bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
    )
    return [(icon, icon, icon, icon, idx) for idx, icon in enumerate(enum_icons.keys())]


########################################################################################
# Operators
########################################################################################


@catalogue.bpy_register
class SHELFMADE_OT_AddShelf(Operator, io_utils.ImportHelper):
    """Add a directory to be included when scanning for scripts"""

    bl_idname = "shelfmade.add_shelf"
    bl_label = "Add Shelf"
    bl_options = {"INTERNAL"}

    directory: StringProperty(name="Directory", subtype="DIR_PATH")

    def invoke(self, context: Context, event: Event):
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context: Context):
        if TYPE_CHECKING:
            shelf: shelf.Shelf

        # Add a new shelf
        shelf = preferences.Preferences.this().shelves.add()

        # Set its directory and name
        if self.directory:
            shelf.directory = self.directory
            shelf.name = Path(self.directory).name

        # Save userprefs
        bpy.ops.wm.save_userpref()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_CleanShelves(Operator):
    """Clean data for all missing shelves and scripts"""

    bl_idname = "shelfmade.clean_shelves"
    bl_label = "Clean Unavailable Shelves & Scripts"
    bl_options = {"INTERNAL"}

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: Context):
        # Clean
        preferences.Preferences.this().initialize_shelves()
        preferences.Preferences.this().clean()

        # Save userprefs
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()
        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_CallScriptMenu(Operator):
    """Open the menu for this script"""

    bl_idname = "shelfmade.call_script_menu"
    bl_label = "Call Script Menu"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index")
    script: StringProperty(name="Script Name")
    mode: EnumProperty(
        items=(
            ("RENAME", "Rename", "Rename this script", "FONT_DATA", 0),
            ("ICON", "Set Icon", "Set this script's icon", "BRUSH_DATA", 1),
            ("OPEN", "Open", "Open this script in the editor", "GREASEPENCIL", 2),
            ("UP", "Move Up", "Move this script up in the list", "TRIA_UP", 3),
            ("DOWN", "Move Down", "Move this script down in the list", "TRIA_DOWN", 4),
        ),
        name="Mode",
    )

    def execute(self, context: Context):
        if self.mode == "RENAME":
            bpy.ops.shelfmade.rename_script(
                "INVOKE_DEFAULT",
                index=self.index,
                script=self.script,
            )

        elif self.mode == "ICON":
            bpy.ops.shelfmade.set_script_icon(
                "INVOKE_DEFAULT",
                index=self.index,
                script=self.script,
            )

        elif self.mode == "OPEN":
            bpy.ops.wm.open_script(
                "EXEC_DEFAULT",
                filepath=str(
                    preferences.Preferences.this()
                    .shelves[self.index]
                    .script_path(script=self.script)
                ),
            )

        elif self.mode in {"DOWN", "UP"}:
            bpy.ops.shelfmade.move_script(
                "EXEC_DEFAULT",
                index=self.index,
                script=self.script,
                direction=self.mode,
            )

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_CallShelfMenu(Operator):
    """Call the menu for this shelf"""

    bl_idname = "shelfmade.call_shelf_menu"
    bl_label = "Call Shelf Menu"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index")
    mode: EnumProperty(
        items=(
            ("RENAME", "Rename", "Rename this shelf", "FONT_DATA", 0),
            ("ICON", "Set Icon", "Set this shelf's icon", "BRUSH_DATA", 1),
            ("VISIBILITY", "Display Options", "Edit display options", "VIS_SEL_11", 2),
            ("OPEN", "Open Folder", "Open this shelf's folder", "FILE_FOLDER", 3),
            ("REMOVE", "Remove", "Remove this shelf", "X", 4),
            ("UP", "Move Up", "Move this shelf up in the list", "TRIA_UP", 5),
            ("DOWN", "Move Down", "Move this shelf down in the list", "TRIA_DOWN", 6),
        ),
        name="Mode",
    )

    def execute(self, context: Context):
        if self.mode == "RENAME":
            bpy.ops.shelfmade.rename_shelf(
                "INVOKE_DEFAULT",
                index=self.index,
            )

        elif self.mode == "ICON":
            bpy.ops.shelfmade.set_shelf_icon(
                "INVOKE_DEFAULT",
                index=self.index,
            )

        elif self.mode == "VISIBILITY":
            bpy.ops.shelfmade.edit_shelf_visibility(
                "INVOKE_DEFAULT",
                index=self.index,
            )

        elif self.mode == "OPEN":
            bpy.ops.wm.path_open(
                filepath=preferences.Preferences.this().shelves[self.index].directory
            )

        elif self.mode == "REMOVE":
            bpy.ops.shelfmade.remove_shelf(
                "INVOKE_DEFAULT",
                index=self.index,
            )

        elif self.mode in {"DOWN", "UP"}:
            bpy.ops.shelfmade.move_shelf(
                index=self.index,
                direction=self.mode,
            )

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_EditShelfVisibility(Operator):
    """Edit this shelf's panel visibility"""

    bl_idname = "shelfmade.edit_shelf_visibility"
    bl_label = "Edit Shelf Visibility"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index")

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_dialog(self, width=200)

    def draw(self, context: Context):
        draw.shelf_visibility(panel=self, context=context, index=self.index)

    def execute(self, context: Context):
        # Save userprefs
        bpy.ops.wm.save_userpref()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_MoveScript(Operator):
    """Move this script up/down in its shelf"""

    bl_idname = "shelfmade.move_script"
    bl_label = "Move Script"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index")
    script: StringProperty(name="Script Name")
    direction: EnumProperty(
        items=(
            ("UP", "Up", "Up", "TRIA_UP", 0),
            ("DOWN", "Down", "Down", "TRIA_DOWN", 1),
        ),
        name="Direction",
    )

    def execute(self, context: Context):
        scripts = preferences.Preferences.this().shelves[self.index].scripts
        current_index = scripts.find(self.script)

        # Get new index
        new_index = current_index - 1 if self.direction == "UP" else current_index + 1

        # Don't move past first or last position
        if current_index < 0 or current_index >= len(scripts):
            return {"CANCELLED"}

        # Move
        scripts.move(current_index, new_index)

        # Save userprefs
        bpy.ops.wm.save_userpref()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_MoveShelf(Operator):
    """Move this shelf up/down in the shelves list"""

    bl_idname = "shelfmade.move_shelf"
    bl_label = "Move Shelf"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index")
    direction: EnumProperty(
        items=(
            ("UP", "Up", "Up", "TRIA_UP", 0),
            ("DOWN", "Down", "Down", "TRIA_DOWN", 1),
        ),
        name="Direction",
    )

    def execute(self, context: Context):
        shelves = preferences.Preferences.this().shelves
        new_index = None

        # Single steps in the preference editor
        if context.area.ui_type == "PREFERENCES":
            new_index = self.index - 1 if self.direction == "UP" else self.index + 1

            # Don't move past first or last position
            if self.index < 0 or self.index >= len(shelves):
                return {"CANCELLED"}

        # Find the next available position based on shelf visibility in other areas
        else:
            if self.direction == "UP":
                stop = -1
                step = -1
            else:
                stop = len(shelves)
                step = 1
            for i in range(self.index, stop, step):
                if shelves[i].is_visible(context=context):
                    new_index = i

        if new_index == None:
            return {"CANCELLED"}

        # Move
        shelves.move(self.index, new_index)

        # Save userprefs
        bpy.ops.wm.save_userpref()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_OpenScript(Operator, io_utils.ImportHelper):
    """Open this Python script file in the text editor"""

    bl_idname = "wm.open_script"
    bl_label = "Open Script"
    bl_options = {"UNDO"}

    filepath: StringProperty(name="File Path", subtype="FILE_PATH")

    def invoke(self, context: Context, event: Event):
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context: Context):
        script_path = Path(self.filepath)

        # Check the script
        if not script_path.exists():
            print(f"Script file {self.filepath} not found")
            return {"CANCELLED"}

        # Try to find existing text
        script = None
        texts = bpy.data.texts[:]
        for text in texts:
            if utils.same_paths([script_path, text.filepath]):
                script = text
                break

        # Open text via operator
        if not script:
            bpy.ops.text.open(filepath=self.filepath)

            # Find the newly created text datablock
            for text in bpy.data.texts:
                if text not in texts:
                    script = text
                    break

        # Ensure text editor
        area = utils.find_or_create_area(
            context=context,
            type="TEXT_EDITOR",
            direction="VERTICAL",
            factor=0.5,
        )

        # Open script in text editor
        area.spaces[0].text = script

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_Reload(Operator):
    """Re-scan all shelves and build script lists"""

    bl_idname = "shelfmade.reload"
    bl_label = "Reload Shelves & Scripts"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(self, context: Context) -> bool:
        return any(
            [shelf.directory for shelf in preferences.Preferences.this().shelves]
        )

    def execute(self, context: Context):
        # Reload
        preferences.Preferences.this().initialize_shelves()

        # Save userprefs
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_RemoveShelf(Operator):
    """Remove a shelf"""

    bl_idname = "shelfmade.remove_shelf"
    bl_label = "Remove Shelf"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index")
    script: StringProperty(name="Script Name")

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: Context):
        # Remove shelf
        prefs = preferences.Preferences.this()
        prefs.shelves.remove(self.index)

        # Re-initialize existing shelves
        prefs.initialize_shelves()

        # Save userprefs
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_RenameScript(Operator):
    """Change the display name of this script"""

    bl_idname = "shelfmade.rename_script"
    bl_label = "Rename Script"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index")
    script: StringProperty(name="Script Name")
    name: StringProperty(name="New Name")

    def invoke(self, context: Context, event: Event):
        if TYPE_CHECKING:
            script: shelf.Script
            shelf: shelf.Shelf

        # Store current name
        shelf = preferences.Preferences.this().shelves[self.index]
        script = shelf.scripts[self.script]
        self.name = script.display_name

        # Draw dialog
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context):
        if TYPE_CHECKING:
            script: shelf.Script
            shelf: shelf.Shelf

        layout = self.layout
        shelf = preferences.Preferences.this().shelves[self.index]
        script = shelf.scripts[self.script]

        # Original file name
        row_original = layout.row()
        row_original.enabled = False
        row_original.label(text="", icon="FILE")
        row_original.prop(data=script, property="name", text="")

        # Script name
        row_new = layout.row()
        row_new.activate_init = True
        row_new.label(text="", icon="FILE_TEXT")
        row_new.prop(data=self, property="name", text="")

    def execute(self, context: Context):
        if TYPE_CHECKING:
            script: shelf.Script
            shelf: shelf.Shelf

        # Avoid empty name
        if not self.name:
            return {"CANCELLED"}

        # Rename
        shelf = preferences.Preferences.this().shelves[self.index]
        script = shelf.scripts[self.script]
        script.display_name = self.name

        # Save userprefs
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_RenameShelf(Operator):
    """Change the display name of this shelf"""

    bl_idname = "shelfmade.rename_shelf"
    bl_label = "Rename Shelf"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index")
    name: StringProperty(name="New Name")

    def invoke(self, context: Context, event: Event):
        # Store current name
        self.name = preferences.Preferences.this().shelves[self.index].name

        # Draw dialog
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context):
        # Shelf name
        row_new = self.layout.row()
        row_new.activate_init = True
        row_new.label(text="", icon="FILE_TEXT")
        row_new.prop(data=self, property="name", text="")

    def execute(self, context: Context):
        # Avoid empty name
        if not self.name:
            return {"CANCELLED"}

        # Rename
        preferences.Preferences.this().shelves[self.index].name = self.name

        # Save userprefs
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_RunScript(Operator, io_utils.ImportHelper):
    """Execute this Python script file"""

    bl_idname = "wm.run_script"
    bl_label = "Run Script"
    bl_options = {"UNDO"}

    filepath: StringProperty(name="File Path", subtype="FILE_PATH")

    def invoke(self, context: Context, event: Event):
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context: Context):
        # Check the script
        script_path = Path(self.filepath)
        if not script_path.exists():
            print(f"Script file {self.filepath} not found")
            return {"CANCELLED"}

        # Run script
        exec(compile(open(script_path).read(), script_path, "exec"))

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_RunText(Operator):
    """Execute this local text datablock"""

    bl_idname = "wm.run_text"
    bl_label = "Run Text Datablock"
    bl_options = {"UNDO"}

    name: StringProperty(name="Text Name")

    def execute(self, context: Context):
        # Run the local script using the basic operator
        with context.temp_override(edit_text=bpy.data.texts[self.name]):
            bpy.ops.text.run_script()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_SetScriptIcon(Operator):
    """Select an icon for this script"""

    bl_idname = "shelfmade.set_script_icon"
    bl_label = "Set Script Icon"
    bl_options = {"INTERNAL"}
    bl_property = "icon"

    index: IntProperty(name="Shelf Index")
    script: StringProperty(name="Script Name")
    icon: EnumProperty(items=enum_icons, name="Icon")

    def invoke(self, context: Context, event: Event):
        if TYPE_CHECKING:
            script: shelf.Script
            shelf: shelf.Shelf

        # Store current icon
        shelf = preferences.Preferences.this().shelves[self.index]
        script = shelf.scripts[self.script]
        self.icon = script.icon

        # Call search popup
        context.window_manager.invoke_search_popup(self)

        return self.execute(context)

    def execute(self, context: Context):
        if TYPE_CHECKING:
            script: shelf.Script
            shelf: shelf.Shelf

        # Set icon
        shelf = preferences.Preferences.this().shelves[self.index]
        script = shelf.scripts[self.script]
        script.icon = self.icon

        # Save userprefs
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalogue.bpy_register
class SHELFMADE_OT_SetShelfIcon(Operator):
    """Select an icon for this shelf"""

    bl_idname = "shelfmade.set_shelf_icon"
    bl_label = "Set Shelf Icon"
    bl_options = {"INTERNAL"}
    bl_property = "icon"

    index: IntProperty(name="Shelf Index")
    icon: EnumProperty(items=enum_icons, name="Icon")

    def invoke(self, context: Context, event: Event):
        # Store current icon
        self.icon = preferences.Preferences.this().shelves[self.index].icon

        # Call search popup
        context.window_manager.invoke_search_popup(self)

        return self.execute(context)

    def execute(self, context: Context):
        # Set icon
        preferences.Preferences.this().shelves[self.index].icon = self.icon

        # Save userprefs
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}
