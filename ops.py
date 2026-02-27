from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context, Event, OperatorProperties, SpaceTextEditor, Text
    from bpy.stub_internal.rna_enums import OperatorReturnItems

from pathlib import Path

import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty, StringProperty
from bpy.types import Operator
from bpy_extras import io_utils

from . import catalog, draw, preferences, shelf, utils


# Enumerators


def enum_shelves(
    operator: SHELFMADE_OT_SaveTextToShelf,
    context: Context,
) -> list[tuple[str, str, str, str, int]]:
    """
    Return the enumerator containing all availble shelves.

    Args:
        operator (SHELFMADE_OT_SetScriptIcon | SHELFMADE_OT_SetShelfIcon)
        context (Context)

    Returns:
        list[tuple[str, str, str, str, int]]:
          Blender enumerator tuple list; each tuple containing
          - identifier (str)
          - name (str)
          - description (str)
          - icon (str)
          - index (int)
    """
    if TYPE_CHECKING:
        shelves: list[shelf.Shelf]

    shelves = preferences.Preferences.this().shelves

    # No shelves available
    if not shelves:
        return [("NONE", "No Shelf Available", "Add a shelf first", "NONE", 0)]

    # List of shelves
    return [
        (str(idx), shelf.name, shelf.name, shelf.icon, idx)
        for idx, shelf in enumerate(shelves)
        if shelf.is_available
    ]


# Operators


@catalog.bpy_register
class SHELFMADE_OT_AddAuthor(Operator):
    bl_idname = "shelfmade.add_author"
    bl_label = "Add Author"
    bl_description = "Add a user with edit permissions to this shelf"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Add a new author to the shelf. If this is the first author, use the current user

        Args:
            context (Context)

        Returns:
            set[str]: CANCELLED, FINISHED, INTERFACE, PASS_THROUGH, RUNNING_MODAL
        """
        if TYPE_CHECKING:
            author: shelf.Author
            shelf: shelf.Shelf

        # Add a new author
        shelf = preferences.Preferences.this().shelves[self.index]
        author = shelf.authors.add()
        if len(shelf.authors) == 1:
            author.name = utils.get_user()
            shelf.save(context)

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_AddShelf(Operator, io_utils.ImportHelper):
    bl_idname = "shelfmade.add_shelf"
    bl_label = "Add Shelf"
    bl_description = "Add a directory to be included when scanning for scripts"
    bl_options = {"INTERNAL"}

    directory: StringProperty(name="Directory", subtype="DIR_PATH")
    add_to_all_editors: BoolProperty(
        name="Make Available In All Editors",
        description="If disabled, the shelf will be visible in the 3D viewport only",
    )
    use_json: BoolProperty(
        name="Use JSON Config",
        description="Store this shelve's configuration in a JSON file",
        default=True,
    )

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Open the file browser dialog for directory selection.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Add a new shelf and set its directory & name. Save user preferences

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        if TYPE_CHECKING:
            shelf: shelf.Shelf

        # Add a new shelf
        shelf = preferences.Preferences.this().shelves.add()

        # Set its directory and name
        if self.directory:
            shelf.directory = self.directory

        # Set JSON config
        shelf.use_json = self.use_json

        # Set editor visibility
        if self.add_to_all_editors:
            for area_type in draw.AREA_TYPES.keys():
                setattr(shelf, f"enabled_{area_type.lower()}", True)

        # Save user preferences
        bpy.ops.wm.save_userpref()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_CleanShelves(Operator):
    bl_idname = "shelfmade.clean_shelves"
    bl_label = "Clean Unavailable Shelves & Scripts"
    bl_description = "Clean data for all missing shelves and scripts"
    bl_options = {"INTERNAL"}

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Request user confirmation via dialog.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        (Re-)initialize shelves and remove any nonexistent shelves & scripts.
        Save user preferences and redraw the current area's UI.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        # Clean
        preferences.Preferences.this().initialize_shelves()
        preferences.Preferences.this().clean()

        # Save user preferences
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()
        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_CallScriptMenu(Operator):
    bl_idname = "shelfmade.call_script_menu"
    bl_label = "Call Script Menu"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the script's shelf")
    script: StringProperty(name="Script Name", description="Name of the script")
    mode: EnumProperty(
        items=(
            ("RENAME", "Rename...", "Rename this script", "BLANK1", 0),
            ("ICON", "Set Icon...", "Set this script's icon", "BLANK1", 1),
            ("OPEN", "Open Script", "Open this script in the editor", "BLANK1", 2),
            ("UP", "Move Up", "Move this script up in the list", "TRIA_UP", 3),
            ("DOWN", "Move Down", "Move this script down in the list", "TRIA_DOWN", 4),
        ),
        name="Mode",
        description="Action to perform on the script",
    )

    @classmethod
    def description(cls, context: Context, properties: OperatorProperties) -> str:
        """
        Generate a description for the menu.

        Args:
            context (Context)
            properties (OperatorProperties)

        Returns:
            str: Operator description
        """
        match properties.mode:
            case "RENAME":
                return SHELFMADE_OT_RenameScript.bl_description
            case "ICON":
                return SHELFMADE_OT_SetScriptIcon.bl_description
            case "OPEN":
                return SHELFMADE_OT_OpenScript.bl_description
            case "DOWN":
                return SHELFMADE_OT_MoveScript.bl_description + ": Down"
            case "UP":
                return SHELFMADE_OT_MoveScript.bl_description + ": Up"
            case _:
                return "Open the menu for this script"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Run one of the script-editing operators based on the operator's mode enumerator.
        The target script is chosen by shelf index and script name.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        if TYPE_CHECKING:
            script: shelf.Script

        match self.mode:
            case "RENAME":
                bpy.ops.shelfmade.rename_script(  # type: ignore
                    "INVOKE_DEFAULT",
                    index=self.index,
                    script=self.script,
                )

            case "ICON":
                bpy.ops.shelfmade.set_script_icon(  # type: ignore
                    "INVOKE_DEFAULT",
                    index=self.index,
                    script=self.script,
                )

            case "OPEN":
                shelf = preferences.Preferences.this().shelves[self.index]
                script = shelf.scripts[self.script]
                bpy.ops.wm.open_script(  # type: ignore
                    "EXEC_DEFAULT",
                    filepath=script.get_path().as_posix(),
                )

            case "DOWN" | "UP":
                bpy.ops.shelfmade.move_script(  # type: ignore
                    "EXEC_DEFAULT",
                    index=self.index,
                    script=self.script,
                    direction=self.mode,
                )

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_CallShelfMenu(Operator):
    bl_idname = "shelfmade.call_shelf_menu"
    bl_label = "Call Shelf Menu"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")
    mode: EnumProperty(
        items=(
            ("RENAME", "Rename...", "Rename this shelf", "BLANK1", 0),
            ("ICON", "Set Icon...", "Set this shelf's icon", "BLANK1", 1),
            ("OPEN", "Open Folder", "Open this shelf's folder", "BLANK1", 3),
            (
                "VISIBILITY",
                "Display Options...",
                "Edit display options",
                "VIS_SEL_11",
                2,
            ),
            ("LOCK", "Lock...", "Edit lock options", "BLANK1", 4),
            ("REMOVE", "Remove", "Remove this shelf", "X", 5),
            ("UP", "Move Up", "Move this shelf up in the list", "TRIA_UP", 6),
            ("DOWN", "Move Down", "Move this shelf down in the list", "TRIA_DOWN", 7),
        ),
        name="Mode",
        description="Action to perform on the shelf",
    )

    @classmethod
    def description(cls, context: Context, properties: OperatorProperties) -> str:
        """
        Generate a description for the menu.

        Args:
            context (Context)
            properties (OperatorProperties)

        Returns:
            str: Operator description
        """
        match properties.mode:
            case "RENAME":
                return SHELFMADE_OT_RenameShelf.bl_description
            case "ICON":
                return SHELFMADE_OT_SetShelfIcon.bl_description
            case "OPEN":
                return "Open this shelf's folder in the system file explorer"
            case "VISIBILITY":
                return SHELFMADE_OT_EditShelfVisibility.bl_description
            case "LOCK":
                return SHELFMADE_OT_EditShelfLock.bl_description
            case "REMOVE":
                return SHELFMADE_OT_RemoveShelf.bl_description
            case "DOWN":
                return SHELFMADE_OT_MoveShelf.bl_description + ": Down"
            case "UP":
                return SHELFMADE_OT_MoveShelf.bl_description + ": Up"
            case _:
                return "Open the menu for this shelf"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Run one of the shelf-editing operators based on the operator's mode enumerator.
        The target shelf is chosen by index.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        match self.mode:
            case "RENAME":
                bpy.ops.shelfmade.rename_shelf(  # type: ignore
                    "INVOKE_DEFAULT",
                    index=self.index,
                )

            case "ICON":
                bpy.ops.shelfmade.set_shelf_icon(  # type: ignore
                    "INVOKE_DEFAULT",
                    index=self.index,
                )

            case "OPEN":
                bpy.ops.wm.path_open(
                    filepath=preferences.Preferences.this()
                    .shelves[self.index]
                    .directory
                )

            case "VISIBILITY":
                bpy.ops.shelfmade.edit_shelf_visibility(  # type: ignore
                    "INVOKE_DEFAULT",
                    index=self.index,
                )

            case "LOCK":
                bpy.ops.shelfmade.edit_shelf_lock(  # type: ignore
                    "INVOKE_DEFAULT",
                    index=self.index,
                )

            case "REMOVE":
                bpy.ops.shelfmade.remove_shelf(  # type: ignore
                    "INVOKE_DEFAULT",
                    index=self.index,
                )

            case "DOWN" | "UP":
                bpy.ops.shelfmade.move_shelf(  # type: ignore
                    index=self.index,
                    direction=self.mode,
                )

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_EditShelfLock(Operator):
    bl_idname = "shelfmade.edit_shelf_lock"
    bl_label = "Edit Shelf Lock"
    bl_description = "Open shelf's lock settings"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Invoke this operator's properties dialog.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[str]: CANCELLED, FINISHED, INTERFACE, PASS_THROUGH, RUNNING_MODAL
        """
        return context.window_manager.invoke_popup(self, width=200)

    def draw(self, context: Context):
        """
        Draw a dialog containing shelf lock options.

        Args:
            context (Context)
        """
        layout = self.layout
        layout.row().label(text=self.bl_label)
        layout.separator(type="LINE")
        draw.shelf_lock(self, context, index=self.index)

    def cancel(self, context: Context):
        """
        Remove empty authors.
        Save the shelf after settings may have changed in the draw phase.

        Args:
            context (Context)
        """
        if TYPE_CHECKING:
            author: shelf.Author
            shelf: shelf.Shelf

        shelf = preferences.Preferences.this().shelves[self.index]
        offset = len(shelf.authors) - 1
        has_removed_empty = False
        for i, author in enumerate(reversed(shelf.authors)):
            i = offset - i
            if not author.name:
                shelf.authors.remove(i)
                has_removed_empty = True

        if has_removed_empty:
            shelf.save(context)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Save the shelf after settings may have changed in the draw phase.

        Args:
            context (Context)

        Returns:
            set[str]: CANCELLED, FINISHED, INTERFACE, PASS_THROUGH, RUNNING_MODAL
        """
        self.cancel(context)
        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_EditShelfVisibility(Operator):
    bl_idname = "shelfmade.edit_shelf_visibility"
    bl_label = "Edit Shelf Visibility"
    bl_description = "Open shelf's panel visibility & display settings"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Invoke this operator's properties dialog.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        return context.window_manager.invoke_popup(self, width=200)

    def draw(self, context: Context):
        """
        Draw a dialog containing shelf visiblity options. These include settings for
        size, column count and area visibility toggles.

        Args:
            context (Context)
        """
        layout = self.layout
        layout.row().label(text=self.bl_label)
        layout.separator(type="LINE")
        draw.shelf_visibility(panel=self, context=context, index=self.index)

    def cancel(self, context: Context):
        """
        Remove empty authors.
        Save the shelf after settings may have changed in the draw phase.

        Args:
            context (Context)
        """
        # Save user preferences
        bpy.ops.wm.save_userpref()

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Save user preferences after the visibility may have changed in the draw phase.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        self.cancel(context)
        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_MoveScript(Operator):
    bl_idname = "shelfmade.move_script"
    bl_label = "Move Script"
    bl_description = "Move this script's position within its shelf"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")
    script: StringProperty(name="Script Name", description="Name of the script")
    direction: EnumProperty(
        items=(
            ("UP", "Up", "Up", "TRIA_UP", 0),
            ("DOWN", "Down", "Down", "TRIA_DOWN", 1),
        ),
        name="Direction",
        description="Which way to move the script within the list",
    )

    @classmethod
    def description(cls, context: Context, properties: OperatorProperties) -> str:
        """
        Generate the description based on direction.

        Args:
            context (Context)
            properties (OperatorProperties)

        Returns:
            str: Operator description
        """
        return f"Move this script {properties.mode.lower()} within the shelf"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Move a script up or down by one position, based on the direction enumerator.
        The target script is chosen by shelf index and script name.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        if TYPE_CHECKING:
            shelf: shelf.Shelf

        shelf = preferences.Preferences.this().shelves[self.index]
        scripts = shelf.scripts
        current_index = scripts.find(self.script)

        # Get new index
        new_index = current_index - 1 if self.direction == "UP" else current_index + 1

        # Don't move past first or last position
        if current_index < 0 or current_index >= len(scripts):
            return {"CANCELLED"}

        # Move
        scripts.move(current_index, new_index)

        # Save
        shelf.save(context)

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_MoveShelf(Operator):
    bl_idname = "shelfmade.move_shelf"
    bl_label = "Move Shelf"
    bl_description = "Move this shelf's position within the shelf list"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")
    direction: EnumProperty(
        items=(
            ("UP", "Up", "Up", "TRIA_UP", 0),
            ("DOWN", "Down", "Down", "TRIA_DOWN", 1),
        ),
        name="Direction",
        description="Which way to move the shelf within the list",
    )

    @classmethod
    def description(cls, context: Context, properties: OperatorProperties) -> str:
        """
        Generate the description based on direction.

        Args:
            context (Context)
            properties (OperatorProperties)

        Returns:
            str: Operator description
        """
        return f"Move this shelf {properties.mode.lower()} within the shelf list"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Move a shelf up or down, based on the direction enumerator. Moving takes all
        shelves' visibilities into account and the new position is chosen by moving past
        the previous/next visible shelf within the current area.
        The target shelf is chosen by index.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        if TYPE_CHECKING:
            shelf: shelf.Shelf

        shelves = preferences.Preferences.this().shelves
        new_index = None

        # Set the range to look up the new position based on direction
        if self.direction == "UP":
            stop = -1
            step = -1
        else:
            stop = len(shelves)
            step = 1

        # Find the next available position within the defined range
        for i in range(self.index, stop, step):
            # Skip current position
            if i == self.index:
                continue

            # Any visible shelf will do
            shelf = shelves[i]
            if shelf.is_visible(context):
                new_index = i
                break

        # No new position available
        if new_index is None:
            return {"CANCELLED"}

        # Move
        shelves.move(self.index, new_index)

        # Save user preferences
        bpy.ops.wm.save_userpref()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_OpenScript(Operator, io_utils.ImportHelper):
    bl_idname = "wm.open_script"
    bl_label = "Open Script"
    bl_description = "Open this Python script file in the text editor"
    bl_options = {"UNDO"}

    filepath: StringProperty(
        name="File Path",
        description="Path to the script file to open",
        subtype="FILE_PATH",
    )

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Open the file browser dialog for script file selection.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Load a script file as a text datablock into the current blend file, if it is
        not loaded yet. If no text editor is open, split the current area.
        Make the datablock active for the first text editor found.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        if TYPE_CHECKING:
            space: SpaceTextEditor

        script_path = Path(self.filepath)

        # Check the script
        if not script_path.exists():
            print(f"Script file {self.filepath} not found")
            return {"CANCELLED"}

        # Try to find existing text
        script = None
        texts = bpy.data.texts[:]
        for text in texts:
            if utils.same_paths(script_path, text.filepath):
                script = text
                break

        # Open text via operator
        if not script:
            script = utils.open_script_file(filepath=script_path)

        # Ensure text editor
        if context.area.ui_type in draw.AREA_TYPES.keys():
            area = utils.find_or_create_area(
                context=context,
                type="TEXT_EDITOR",
                direction="VERTICAL",
                factor=0.5,
            )

            # Open script in text editor
            space = area.spaces[0]  # type: ignore
            space.text = script

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_Reload(Operator):
    bl_idname = "shelfmade.reload"
    bl_label = "Reload Shelves & Scripts"
    bl_description = "Re-scan all shelves and sync scripts"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        Make the reload button unavailable if there are no scripts with a directory.

        Args:
            context (Context)

        Returns:
            bool: Whether this operator is available or not
        """
        return any(
            [shelf.directory for shelf in preferences.Preferences.this().shelves]
        )

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Reinitialize all shelves. Save user preferences and redraw the current area.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        # Reload
        preferences.Preferences.this().initialize_shelves()

        # Save user preferences
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_RemoveAuthor(Operator):
    bl_idname = "shelfmade.remove_author"
    bl_label = "Remove Author"
    bl_description = "Remove the author from the shelf"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")
    author_index: IntProperty(name="Author Index", description="Position of the author")

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Request user confirmation via dialog.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[str]: CANCELLED, FINISHED, INTERFACE, PASS_THROUGH, RUNNING_MODAL
        """
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Remove an author.

        Args:
            context (Context)

        Returns:
            set[str]: CANCELLED, FINISHED, INTERFACE, PASS_THROUGH, RUNNING_MODAL
        """
        if TYPE_CHECKING:
            shelf: shelf.Shelf

        # Remove author
        shelf = preferences.Preferences.this().shelves[self.index]
        shelf.authors.remove(self.author_index)
        shelf.save(context)

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_RemoveShelf(Operator):
    bl_idname = "shelfmade.remove_shelf"
    bl_label = "Remove Shelf"
    bl_description = "Remove this shelf (does not delete any files)"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Request user confirmation via dialog.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Remove a shelf. Re-initialize shelves afterwards, save user preferences and
        redraw the current area.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        # Remove shelf
        prefs = preferences.Preferences.this()
        prefs.shelves.remove(self.index)

        # Re-initialize existing shelves
        prefs.initialize_shelves()

        # Save user preferences
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_RenameScript(Operator):
    bl_idname = "shelfmade.rename_script"
    bl_label = "Rename Script"
    bl_description = "Change the display name of this script"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")
    script: StringProperty(name="Script Name", description="Name of the script")

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Invoke the name popup.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        return context.window_manager.invoke_popup(self, width=200)

    def draw(self, context: Context):
        """
        Draw a dialog displaying the script's file name, as well as an input property
        for its new display name.

        Args:
            context (Context)
        """
        if TYPE_CHECKING:
            script: shelf.Script
            shelf: shelf.Shelf

        layout = self.layout
        layout.row().label(text=self.bl_label)
        layout.separator(type="LINE")

        layout = self.layout
        shelf = preferences.Preferences.this().shelves[self.index]
        script = shelf.scripts[self.script]

        # Original file name
        row_original = layout.row()
        row_original.enabled = False
        row_original.label(text="", icon="FILE")
        row_original.prop(script, "name", text="")

        # Script name
        row_new = layout.row()
        row_new.activate_init = True
        row_new.label(text="", icon="FILE_TEXT")
        row_new.prop(script, "display_name", text="")

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Dummy.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_RenameShelf(Operator):
    bl_idname = "shelfmade.rename_shelf"
    bl_label = "Rename Shelf"
    bl_description = "Change the display name of this shelf"
    bl_options = {"INTERNAL"}

    index: IntProperty(name="Shelf Index", description="Position of the shelf")

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Invoke the name popup.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        return context.window_manager.invoke_popup(self, width=200)

    def draw(self, context: Context):
        """
        Draw the user input field for the shelf display name.

        Args:
            context (Context)
        """
        layout = self.layout
        layout.row().label(text=self.bl_label)
        layout.separator(type="LINE")

        shelf = preferences.Preferences.this().shelves[self.index]

        # Shelf name
        row_new = self.layout.row()
        row_new.activate_init = True
        row_new.label(text="", icon="FILE_TEXT")
        row_new.prop(shelf, "name", text="")

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Dummy.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_RunScript(Operator, io_utils.ImportHelper):
    bl_idname = "wm.run_script"
    bl_label = "Run Script"
    bl_options = {"UNDO"}

    filepath: StringProperty(
        name="File Path",
        description="Path to the script file to run",
        subtype="FILE_PATH",
    )

    @classmethod
    def description(cls, context: Context, properties: OperatorProperties) -> str:
        """
        Generate a description from the filepath property.

        Args:
            context (Context)
            properties (OperatorProperties)

        Returns:
            str: Operator description
        """
        if properties.filepath:
            return f"Execute Python script: {Path(properties.filepath).name}"
        return "Execute a Python script"

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Open the file browser dialog for script file selection.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Load a script file as a text datablock into the current blend file. Run it and
        remove it right after. Raise any exceptions that might have occured afterwards.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        # Check the script
        script_path = Path(self.filepath)
        if not script_path.exists():
            print(f"Script file {self.filepath} not found")
            return {"CANCELLED"}

        # Exception store
        exception = None

        # Run script
        text = utils.open_script_file(filepath=script_path)
        with context.temp_override(edit_text=text):
            try:
                bpy.ops.text.run_script()

            # If the script causes an exception, store it for later
            except Exception as e:
                exception = e

        # Remove script
        try:
            bpy.data.texts.remove(text)
        except ReferenceError:
            print("Could not delete script, already removed")

        # Raise potential exception after cleanup
        if exception:
            raise exception

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_RunText(Operator):
    bl_idname = "wm.run_text"
    bl_label = "Run Text Datablock"
    bl_description = "Execute this local text datablock"
    bl_options = {"UNDO"}

    name: StringProperty(
        name="Text Name",
        description="Name of the text datablock to run",
    )

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Run a text datablock from within the current blend file.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        # Run the local script using the basic operator
        with context.temp_override(edit_text=bpy.data.texts[self.name]):
            bpy.ops.text.run_script()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_SaveTextToShelf(Operator):
    bl_idname = "text.save_text_to_shelf"
    bl_label = "Save To Shelf"
    bl_description = "Save this text datablock to a shelf directory"
    bl_options = {"INTERNAL"}

    shelf: EnumProperty(
        items=enum_shelves,  # type: ignore
        name="Shelf",
        description="Name of the shelf to save the script to",
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        Make this operator availble in the text editor if there's an active text
        datablock.

        Args:
            context (Context)

        Returns:
            bool: Whether this operator is available or not
        """
        if TYPE_CHECKING:
            space: SpaceTextEditor | None

        space = context.space_data  # type: ignore
        return bool(context.area.type == "TEXT_EDITOR" and space.text)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Save the currently opened text datablock to selected shelf.
        Re-initiate the shelf. Save user preferences

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        if TYPE_CHECKING:
            shelf: shelf.Shelf
            text: Text | None
            space: SpaceTextEditor

        # Cancel if no shelves are available
        if self.shelf == "NONE":
            return {"CANCELLED"}

        # Ensure python extension
        space = context.space_data  # type: ignore
        if not space:
            return {"CANCELLED"}
        text = space.text
        if not text:
            return {"CANCELLED"}
        if not text.name.endswith(".py"):
            text.name += ".py"

        # Save text
        shelf = preferences.Preferences.this().shelves[int(self.shelf)]
        filepath = Path(shelf.directory, text.name).as_posix()
        bpy.ops.text.save_as("EXEC_DEFAULT", filepath=filepath)

        # Reload shelf
        shelf.initialize()

        # Save user preferences
        bpy.ops.wm.save_userpref()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_SetScriptIcon(Operator):
    bl_idname = "shelfmade.set_script_icon"
    bl_label = "Set Script Icon"
    bl_description = "Select an icon for this script from Blender's internal icon set"
    bl_options = {"INTERNAL"}
    bl_property = "icon"

    index: IntProperty(name="Shelf Index", description="Position of the shelf")
    script: StringProperty(name="Script Name", description="Name of the script")
    icon: EnumProperty(
        items=utils.enum_icons,  # type: ignore
        name="Icon",
        description="Name of the icon to set for the script",
    )

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Store the current script icon and invoke the icon enumerator search popup.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
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

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Set a script's icon (string). Save user preferences and redraw the current area.
        The target script is chosen by shelf index and script name.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        if TYPE_CHECKING:
            script: shelf.Script
            shelf: shelf.Shelf

        # Set icon
        shelf = preferences.Preferences.this().shelves[self.index]
        script = shelf.scripts[self.script]
        script.icon = self.icon

        # Save user preferences
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}


@catalog.bpy_register
class SHELFMADE_OT_SetShelfIcon(Operator):
    bl_idname = "shelfmade.set_shelf_icon"
    bl_label = "Set Shelf Icon"
    bl_description = "Select an icon for this shelf from Blender's internal icon set"
    bl_options = {"INTERNAL"}
    bl_property = "icon"

    index: IntProperty(name="Shelf Index", description="Position of the shelf")
    icon: EnumProperty(
        items=utils.enum_icons,  # type: ignore
        name="Icon",
        description="Name of the icon to set for the shelf",
    )

    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        """
        Store the current shelf icon and invoke the icon enumerator search popup.

        Args:
            context (Context)
            event (Event)

        Returns:
            set[OperatorReturnItems]
        """
        # Store current icon
        self.icon = preferences.Preferences.this().shelves[self.index].icon

        # Call search popup
        context.window_manager.invoke_search_popup(self)

        return self.execute(context)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        """
        Set a shelf's icon (string). Save user preferences and redraw the current area.
        The target shelf is chosen by index.

        Args:
            context (Context)

        Returns:
            set[OperatorReturnItems]
        """
        # Set icon
        preferences.Preferences.this().shelves[self.index].icon = self.icon

        # Save user preferences
        bpy.ops.wm.save_userpref()

        # Redraw UI
        context.area.tag_redraw()

        return {"FINISHED"}
