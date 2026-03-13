from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal

    from bpy.types import bpy_struct, Context, Operator, Panel, Text, UILayout
    from bpy.stub_internal.rna_enums import IconItems

    from .shelf import Author, Script, Shelf

import re

import bpy

from . import preferences, utils

# Dictionary containing 'area.ui_type' keys and area icon values
AREA_TYPES: dict[str, IconItems] = {
    "VIEW_3D": "VIEW3D",
    "IMAGE_EDITOR": "IMAGE",
    "UV": "UV",
    "CompositorNodeTree": "NODE_COMPOSITING",
    "TextureNodeTree": "NODE_TEXTURE",
    "GeometryNodeTree": "GEOMETRY_NODES",
    "ShaderNodeTree": "NODE_MATERIAL",
    "SEQUENCE_EDITOR": "SEQUENCE",
    "CLIP_EDITOR": "TRACKER",
    "DOPESHEET": "ACTION",
    "TIMELINE": "TIME",
    "FCURVES": "GRAPH",
    "DRIVERS": "DRIVER",
    "NLA_EDITOR": "NLA",
    "TEXT_EDITOR": "TEXT",
    # "CONSOLE": "CONSOLE",
    # "INFO": "INFO",
    # "OUTLINER": "OUTLINER",
    # "PROPERTIES": "PROPERTIES",
    # "FILES": "FILEBROWSER",
    # "ASSETS": "ASSET_MANAGER",
    "SPREADSHEET": "SPREADSHEET",
    # "PREFERENCES": "PREFERENCES",
}


def foldout(
    layout: UILayout,
    data: bpy_struct,
    property: str,
    *,
    text: str | None = None,
    alignment: Literal["LEFT", "CENTER", "RIGHT"] = "LEFT",
    icon: IconItems | None = None,
) -> bool:
    """
    Draw a foldout control in the current UI.

    Args:
        layout (UILayout): Layout to draw at
        data (bpy_struct): Host struct of the bool prop that holds the collapse status
        property (str): Name of bool property that holds the collapse status
        text (str | None): Alternative text for label
        alignment (str):
          - LEFT
          - CENTER
          - RIGHT
        icon (str | None): Draw an additional icon

    Returns:
        bool: Whether the foldout should be drawn or not
    """
    enabled = bool(getattr(data, property))

    row_main = layout.row(align=True)

    # Button, add text if left
    has_icon = icon is not None and icon != "NONE"
    row_button = row_main.row(align=True)
    row_button.alignment = "LEFT"
    row_button.prop(
        data,
        property,
        text=text if alignment == "LEFT" and not has_icon else "",
        icon_only=False if alignment == "LEFT" or has_icon else True,
        icon="DOWNARROW_HLT" if enabled else "RIGHTARROW",
        emboss=False,
    )

    # Text in separate property if not left aligned, to be able to separate from button
    if alignment != "LEFT" or icon:
        row_text = row_main.row(align=True)
        row_text.alignment = alignment
        row_text.prop(
            data,
            property,
            text=text,
            icon=icon,
            toggle=True,
            emboss=False,
        )

    return enabled


def local_scripts(panel: Panel | Operator, context: Context):
    """
    Draw all python script text datablocks found in the currently loaded blend file.

    Args:
        panel (Panel | Operator)
        context (Context)
    """
    layout = panel.layout

    # Draw script buttons
    for text in bpy.data.texts:
        # Only draw python scripts
        if not text.name.endswith(".py"):
            continue

        # Generate name without .py
        name = text.name
        match = re.match(pattern=r"(.*)\.py$", string=name)
        if match:
            name = match.groups()[0]

        # Draw operator
        layout.row().operator(
            "wm.run_text",
            text=text.name,
        ).name = text.name


def shelf_lock(panel: Panel | Operator, context: Context, index: int):
    """
    Draw an interface containing shelf lock options.

    Args:
        panel (Panel | Operator)
        context (Context)
        shelf (int): Index of the shelf whose settings are drawn
    """
    if TYPE_CHECKING:
        author: Author
        shelf: Shelf

    shelf = preferences.Preferences.this().shelves[index]
    is_unlockable = shelf.is_unlockable()
    layout = panel.layout

    # Lock
    row_lock = layout.row()
    row_lock.enabled = is_unlockable
    row_lock.prop(
        shelf,
        "is_locked",
        toggle=True,
        icon="LOCKED" if shelf.is_locked else "UNLOCKED",
    )

    # Authors info
    layout.separator()
    row_info = layout.row()
    row_info.alignment = "CENTER"
    if is_unlockable:
        text = "Add authors to limit unlocking"
        icon = "INFO"
    else:
        text = "You are not in the authors list"
        icon = "ERROR"
    row_info.label(text=text, icon=icon)

    # Add authors
    col_lock = layout.column(align=True)
    if is_unlockable:
        col_lock.separator()
        col_lock.row(align=True).operator(
            "shelfmade.add_author",
            icon="PLUS",
        ).index = index
        if shelf.is_locked:
            col_lock.enabled = False
    else:
        col_lock.enabled = False

    # Authors list
    if not shelf.authors:
        return
    user = utils.get_user()
    box_authors = col_lock.box()
    for i, author in enumerate(shelf.authors):
        row_author = box_authors.row(align=True)

        # Name
        row_name = row_author.row(align=True)
        row_name.prop(author, "name", text="")
        if not is_unlockable:
            continue
        row_remove = row_author.row(align=True)
        if user == author.name:
            row_name.enabled = False

        # Remove
        op_remove = row_remove.operator(
            "shelfmade.remove_author",
            text="",
            icon="X",
            # emboss=False,
        )
        op_remove.index = index
        op_remove.author_index = i
        if user == author.name and len(shelf.authors) > 1:
            row_remove.enabled = False


def script_options(
    panel: Panel | Operator,
    context: Context,
    index: int,
    script: str,
):
    """
    Draw an interface containing script display options.

    Args:
        panel (Panel | Operator)
        context (Context)
        shelf (int): Index of the shelf containing the script
        script (str): Name of the script whose settings are drawn
    """
    if TYPE_CHECKING:
        script: Script

    scripts = preferences.Preferences.this().shelves[index].scripts
    nb_position = scripts.find(script)

    script = scripts[script]
    layout = panel.layout

    # Name & icon
    row_name = layout.row(align=True)
    row_name.operator_context = "INVOKE_DEFAULT"
    op_icon = row_name.operator(
        "shelfmade.set_script_icon",
        text="",
        icon="BLANK1" if script.icon == "NONE" else script.icon,
    )
    op_icon.index = index
    op_icon.script = script.name
    row_name.prop(script, "display_name", text="")

    layout.separator()
    box_display = layout.box()

    # Attach
    row_attach = box_display.row()
    row_attach.alignment = "CENTER"
    row_attach.prop(script, "use_attach", text="Attach to Previous Row")

    # Spacing
    col_spacing = box_display.column()
    col_spacing.use_property_split = True
    col_spacing.prop(script, "spacing", expand=True)

    # Styling
    col_style = box_display.column()
    col_style.use_property_split = True
    col_style.prop(script, "style", expand=True)

    # Height
    row_height = box_display.row()
    row_height.prop(script, "height", slider=True)

    # Disable unavailable options
    row_attach.enabled = col_spacing.enabled = nb_position != 0

    layout.separator()

    # Move
    op_up = layout.operator(
        "shelfmade.move_script",
        text="Move Up",
        icon="TRIA_UP",
    )
    op_up.index = index
    op_up.script = script.name
    op_up.direction = "UP"
    op_down = layout.operator(
        "shelfmade.move_script",
        text="Move Down",
        icon="TRIA_DOWN",
    )
    op_down.index = index
    op_down.script = script.name
    op_down.direction = "DOWN"


def shelf_visibility(panel: Panel | Operator, context: Context, index: int):
    """
    Draw an interface containing shelf visiblity options.

    Args:
        panel (Panel | Operator)
        context (Context)
        shelf (int): Index of the shelf whose settings are drawn
    """
    if TYPE_CHECKING:
        shelf: Shelf

    shelf = preferences.Preferences.this().shelves[index]
    layout = panel.layout

    # Area type toggles
    col_areas = layout.column()
    for area_type, icon in AREA_TYPES.items():
        # Area type row
        row_area = col_areas.row()
        row_area.alignment = "LEFT"

        # Area type toggle
        property = f"enabled_{area_type.lower()}"
        row_area.prop(shelf, property, text="")
        row_area.prop(shelf, property, icon=icon, emboss=False)


def shelf_scripts(panel: Panel | Operator, context: Context):
    """
    Draw all shelves that are visible in the current area.
    Wrap their respective script run operators in expander toggle boxes.
    If there are no shelves, draw the 'Add Shelf' operator button instead.

    Args:
        panel (Panel | Operator)
        context (Context)
    """
    if TYPE_CHECKING:
        script: Script
        shelf: Shelf
        row_main: UILayout

    layout = panel.layout
    prefs = preferences.Preferences.this()
    shelves = prefs.shelves
    if not shelves:
        layout.operator("shelfmade.add_shelf", icon="ADD")
        return

    # Draw each shelf
    for sh_i, shelf in enumerate(shelves):
        if not shelf.is_visible(context):
            continue

        col_shelf = layout.box().column(align=True)
        row_title = col_shelf.row()

        # Shelf title & expander
        if foldout(
            row_title,
            shelf,
            "show_scripts",
            text=shelf.name,
            alignment="LEFT",
            icon=None if shelf.icon == "NONE" else shelf.icon,
        ):
            # Don't draw if scripts are empty
            scripts = [s for s in shelf.scripts if s.is_available]
            if scripts:
                # Draw script buttons
                for sc_i, script in enumerate(scripts):
                    # Create script row and set height
                    if sc_i == 0 or not script.use_attach:
                        # Separate from last row
                        if sc_i == 0:
                            col_shelf.separator()
                        elif script.spacing != "ALIGN":
                            col_shelf.separator(
                                factor=2 if script.spacing in {"SPACE", "LINE"} else 1,
                                type="LINE" if script.spacing == "LINE" else "SPACE",
                            )

                        # Create main UI row
                        row_main = col_shelf.row(align=True)

                    # Separate from last button in row
                    elif script.spacing != "ALIGN":
                        row_main.separator(  # type: ignore
                            factor=2 if script.spacing in {"SPACE", "LINE"} else 1,
                            type="LINE" if script.spacing == "LINE" else "SPACE",
                        )

                    # Script operator
                    row_script = row_main.row(align=True)  # type: ignore
                    row_script.scale_y = script.height
                    row_op = row_script.row(align=True)
                    row_op.operator_context = "EXEC_DEFAULT"
                    row_op.alert = script.style in {
                        "ALERT",
                        "EMBOSS_ALERT",
                    }
                    row_op.emboss = (
                        "NONE" if script.style in {"NONE", "ALERT"} else "NORMAL"
                    )
                    op_script = row_op.operator(
                        "wm.run_script",
                        text=script.display_name,
                        icon=script.icon,
                        depress=script.style == "DEPRESS",
                    )
                    op_script.filepath = script.get_path().as_posix()
                    op_script.index = sh_i
                    op_script.script = script.name

                    # Menu button
                    if not shelf.is_locked and prefs.show_menus:
                        row_script.operator_context = "INVOKE_DEFAULT"
                        op_script = row_script.operator(
                            "shelfmade.show_script_options",
                            text="",
                            icon="PROP_ON" if script.is_focused else "DOWNARROW_HLT",
                            emboss=False,
                        )
                        op_script.index = sh_i
                        op_script.script = script.name

            else:
                row_noscripts = col_shelf.row()
                row_noscripts.alignment = "CENTER"
                row_noscripts.label(text="No Scripts Found", icon="GHOST_DISABLED")

        # Shelf menu
        row_menu = row_title.row()
        row_menu.alignment = "RIGHT"
        if not prefs.show_menus:
            row_menu.label(text="", icon="BLANK1")
        elif shelf.is_locked:
            row_menu.operator_context = "INVOKE_DEFAULT"
            row_menu.operator(
                "shelfmade.edit_shelf_lock",
                text="",
                icon="LOCKED",
                emboss=False,
            ).index = sh_i
        else:
            row_menu.operator_menu_enum(
                "shelfmade.call_shelf_menu",
                "mode",
                text="",
                icon="COLLAPSEMENU",
            ).index = sh_i


def text_editor_shelf_menu(panel: Panel | Operator, context: Context):
    """
    Draw additional menu buttons the text editor.

    Args:
        panel (Panel | Operator)
        context (Context)
    """
    if TYPE_CHECKING:
        shelves: list[Shelf]
        text: Text

    # Get active text
    try:
        text = context.space_data.text  # type: ignore
    except AttributeError:
        return
    if not text:
        return

    layout = panel.layout

    # Draw 'save' button if text is already in a shelf
    filepath = bpy.path.abspath(text.filepath)
    shelves = preferences.Preferences.this().shelves
    for shelf in shelves:
        if shelf.path_is_in_shelf(filepath):
            layout.operator(
                "text.save",
                text=shelf.name,
                icon=shelf.icon,
            )
            return

    # Draw 'save to shelf' operator
    layout.operator_menu_enum(
        "text.save_text_to_shelf",
        "shelf",
        text="To Shelf",
    )
