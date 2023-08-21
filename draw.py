from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal
    from bpy.types import Context, ID, Panel, Text, UILayout
    from .shelf import Script, Shelf

import bpy
import re
from . import preferences


########################################################################################
# Statics
########################################################################################


# Dictionary containing 'area.ui_type' keys and area icon values
AREA_TYPES = {
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


########################################################################################
# Draw functions
########################################################################################


def local_scripts(panel: Panel, context: Context):
    """
    Draw all python script text datablocks found in the currently loaded blend file.

    Parameters:
        - panel (Panel)
        - context (Context)
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
            operator="wm.run_text",
            text=text.name,
        ).name = text.name


def shelf_visibility(panel: Panel, context: Context, index: int):
    """
    Draw an interface containing shelf visiblity options. These include settings for
    size, column count and area visibility toggles.

    Parameters:
        - panel (Panel)
        - context (Context)
        - shelf (int): Index of the shelf whose settings are drawn
    """
    if TYPE_CHECKING:
        shelf: Shelf

    shelf = preferences.Preferences.this().shelves[index]
    layout = panel.layout

    # Size and columns
    box_size = layout.box()
    box_size.prop(data=shelf, property="height", slider=True)
    box_size.prop(data=shelf, property="columns")
    row_align = box_size.row()
    row_align.alignment = "CENTER"
    row_align.prop(data=shelf, property="align")

    # Area type toggles
    col_areas = layout.column()
    for area_type, icon in AREA_TYPES.items():
        # Area type row
        row_area = col_areas.row()
        row_area.alignment = "LEFT"

        # Area type toggle
        property = f"enabled_{area_type.lower()}"
        row_area.prop(data=shelf, property=property, text="")
        row_area.prop(data=shelf, property=property, icon=icon, emboss=False)


def shelf_scripts(panel: Panel, context: Context):
    """
    Draw all shelves that are visible in the current area.
    Wrap their respective script run operators in expander toggle boxes.
    If there are no shelves, draw the 'Add Shelf' operator button instead.

    Parameters:
        - panel (Panel)
        - context (Context)
    """
    if TYPE_CHECKING:
        script: Script
        shelf: Shelf
        row_script: UILayout

    layout = panel.layout
    prefs = preferences.Preferences.this()
    shelves = prefs.shelves
    if not shelves:
        layout.operator(operator="shelfmade.add_shelf", icon="ADD")
        return

    # Draw each shelf
    for sh_i, shelf in enumerate(shelves):
        if not shelf.is_visible(context=context):
            continue

        box_shelf = layout.box()
        row_title = box_shelf.row()

        # Shelf title & expander
        if show_layout(
            layout=row_title,
            data=shelf,
            property="show_scripts",
            text=shelf.name,
            alignment="LEFT",
            icon="" if shelf.icon == "NONE" else shelf.icon,
        ):
            # Don't draw if scripts are empty
            scripts = [s for s in shelf.scripts if s.is_available]
            if scripts:

                # Generate grid flow
                grid_shelf = box_shelf.grid_flow(
                    columns=shelf.columns,
                    even_columns=True,
                    even_rows=True,
                    align=shelf.align,
                )
                columns = []
                for _ in range(0, shelf.columns):
                    columns.append(grid_shelf.column(align=shelf.align))

                # Draw script buttons
                for sc_i, script in enumerate(scripts):

                    # Assign to column & set height
                    row_script = columns[sc_i % shelf.columns].row(align=True)
                    row_script.scale_y = shelf.height

                    # Run script operator
                    row_script.operator_context = "EXEC_DEFAULT"
                    row_script.operator(
                        operator="wm.run_script",
                        text=script.display_name,
                        icon=script.icon,
                    ).filepath = str(shelf.script_path(script=script.name))

                    # Menu button
                    if not prefs.is_locked:
                        op_script = row_script.operator_menu_enum(
                            operator="shelfmade.call_script_menu",
                            property="mode",
                            text="",
                        )
                        op_script.index = sh_i
                        op_script.script = script.name

            else:
                row_noscripts = box_shelf.row()
                row_noscripts.alignment = "CENTER"
                row_noscripts.label(text="No Scripts Found", icon="GHOST_DISABLED")

        # Shelf menu
        if not prefs.is_locked:
            row_menu = row_title.row()
            row_menu.alignment = "RIGHT"
            row_menu.operator_menu_enum(
                operator="shelfmade.call_shelf_menu",
                property="mode",
                text="",
                icon="COLLAPSEMENU",
            ).index = sh_i


def show_layout(
    layout: UILayout,
    data: ID,
    property: str,
    text: str | None = None,
    alignment: Literal["LEFT", "CENTER", "RIGHT"] = "LEFT",
    icon: str = "",
) -> bool:
    """
    Draw a foldout control in the current UI.

    Parameters:
        - layout (UILayout): Layout to draw at
        - data (ID): Host datablock of the bool property that holds the
          collapse status
        - property (str): Name of bool property that holds the collapse status
        - text (str | None): Alternative text for label
        - alignment (str):
            - LEFT
            - CENTER
            - RIGHT
        - icon (str): Draw an additional icon

    Returns:
        - bool: Whether the foldout should be drawn or not
    """
    enabled = bool(getattr(data, property))

    row_main = layout.row(align=True)

    # Button, add text if left
    row_button = row_main.row(align=True)
    row_button.alignment = "LEFT"
    row_button.prop(
        data=data,
        property=property,
        text=text if alignment == "LEFT" and not icon else "",
        icon_only=False if alignment == "LEFT" or icon else True,
        icon="DOWNARROW_HLT" if enabled else "RIGHTARROW",
        emboss=False,
    )

    # Text in separate property if not left aligned, to be able to separate from button
    if alignment != "LEFT" or icon:
        row_text = row_main.row(align=True)
        row_text.alignment = alignment
        row_text.prop(
            data=data,
            property=property,
            text=text,
            icon=icon or "NONE",
            toggle=True,
            emboss=False,
        )

    return enabled


def text_editor_shelf_menu(panel: Panel, context: Context):
    """
    Draw additional menu buttons the text editor.

    Parameters:
        - panel (Panel)
        - context (Context)
    """
    if TYPE_CHECKING:
        shelves: list[Shelf]
        text: Text

    # Get active text
    text = context.space_data.text
    if not text:
        return

    layout = panel.layout

    # Draw 'save' button if text is already in a shelf
    filepath = bpy.path.abspath(text.filepath)
    shelves = preferences.Preferences.this().shelves
    for shelf in shelves:
        if shelf.path_is_in_shelf(path=filepath):
            layout.operator(
                operator="text.save",
                text=shelf.name,
                icon=shelf.icon,
            )
            return

    # Draw 'save to shelf' operator
    layout.operator_menu_enum(
        operator="text.save_text_to_shelf",
        property="shelf",
        text="To Shelf",
    )
