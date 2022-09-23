from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context, Panel


import bpy
import re
from . import preferences

########################################################################################
# Draw functions
########################################################################################


def directory_scripts(panel: Panel, context: Context):
    """
    Draw all scripts generated from the scripts directory.

    Parameters:
        - panel (Panel)
        - context (Context)
    """
    layout = panel.layout

    # Get preferences
    prefs = preferences.Preferences.this

    # Draw script buttons
    for i, script in enumerate(prefs.scripts):
        row_script = layout.row(align=True)

        # Run script operator
        row_script.operator(
            operator="wm.shelfmade_run_script",
            text=script.name,
        ).index = i

        # Edit button
        if prefs.show_edit_buttons:
            row_script.operator(
                operator="wm.shelfmade_edit_script",
                text="",
                icon="GREASEPENCIL",
            ).index = i


def local_scripts(panel: Panel, context: Context):
    """
    Draw all scripts generated from the scripts directory.

    Parameters:
        - panel (Panel)
        - context (Context)
    """
    layout = panel.layout

    # Draw script buttons
    for i, text in enumerate(bpy.data.texts):

        # Generate name without .py
        name = text.name
        match = re.match(pattern=r"(.*)\.py$", string=name)
        if match:
            name = match.groups()[0]

        # Draw operator
        layout.row().operator(
            operator="wm.shelfmade_run_text",
            text=text.name,
        ).index = i


def settings(panel: Panel, context: Context):
    """
    Draw the directory settings.

    Parameters:
        - panel (Panel)
        - context (Context)
    """
    layout = panel.layout
    col_settings = layout.column(align=True)
    row_directory = col_settings.row(align=True)

    # Get preferences
    prefs = preferences.Preferences.this

    # Reload button
    row_directory.operator(
        operator="wm.shelfmade_reload_scripts",
        text="",
        icon="FILE_REFRESH",
    )

    # Directory path
    row_directory.prop(data=prefs, property="script_directory", icon_only=True)

    # Show edit buttons
    row_edit = col_settings.box().row()
    row_edit.alignment = "CENTER"
    row_edit.prop(data=prefs, property="show_edit_buttons")
