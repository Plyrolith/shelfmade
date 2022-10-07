from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Literal
    from bpy.types import Area, Context, Text

import bpy
from pathlib import Path


########################################################################################
# Utilities
########################################################################################


def find_area_by_type(context: Context, type: str) -> Area | None:
    """
    Finds an area that fits given area type. If none is available, creates a new area
    by splitting the current one.

    Parameters:
        - context (Context)
        - type (str): Area type to look for

    Returns:
        - Area | None: First area of given type, if any exist
    """
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == type:
                return area


def find_or_create_area(
    context: Context,
    type: str,
    direction: Literal["HORIZONTAL", "VERTICAL"],
    factor: float,
) -> Area:
    """
    Finds an area that fits given area type. If none is available, creates a new area
    by splitting the current one.

    Parameters:
        - context (Context)
        - type (str): Area type to be found or created
        - direction (str): Split direction
            - HORIZONTAL
            - VERTICAL
        - factor (float): How much space newly created area will take

    Returns:
        - Area: Newly created area
    """
    area = find_area_by_type(context=context, type=type)
    if area:
        return area

    return split_area(area=context.area, type=type, direction=direction, factor=factor)


def open_script_file(filepath: str | Path) -> Text:
    """
    Open a file in Blender's text editor.

    Parameters:
        - filepath (str | Path)

    Returns:
        - Text
    """
    # Store existing texts snapshot
    texts = bpy.data.texts[:]

    # Open script from file path
    bpy.ops.text.open(filepath=str(filepath))

    # Find the newly created text datablock
    for text in bpy.data.texts:
        if text not in texts:
            return text


def same_paths(paths: List[str | Path]) -> bool:
    """
    Checks whether a list of paths points to the same file/folder.

    Parameters:
        - paths (list of str | Path): List of paths to compare

    Returns:
        - bool: Whether all paths are the same or not
    """
    assert len(paths) > 1, "Multiple paths needed to compare"

    first_path = None
    for path in paths:
        # If path is a string, guarantee absolute path and convert to pathlib
        if isinstance(path, str):
            path = Path(bpy.path.abspath(path=path))

        # Resolve and convert to posix
        path = path.resolve().as_posix()

        # Store first path for comparison
        if not first_path:
            first_path = path
            continue

        # Compare
        if path != first_path:
            return False

    return True


def split_area(
    area: Area,
    type: str,
    direction: Literal["HORIZONTAL", "VERTICAL"],
    factor: float,
) -> Area:
    """
    Splits the specified area and creates a new area of given input type.

    Parameters:
        - area (Area): Area to split
        - type (str): Area type of the newly created area
        - direction (str): Split direction
            - HORIZONTAL
            - VERTICAL
        - factor (float): How much space newly the created area will take

    Returns:
        - Area: Newly created area
    """
    # Save list of areas to be able to return newly created area
    screen = area.id_data
    start_areas = screen.areas[:]

    # Do split
    with bpy.context.temp_override(area=area):
        bpy.ops.screen.area_split(direction=direction, factor=factor)

    # Return the newly created area
    for area in screen.areas:
        if area not in start_areas:
            area.type = type.upper()
            return area
