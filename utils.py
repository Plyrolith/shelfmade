from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike
    from typing import Literal

    from bpy.stub_internal.rna_enums import SpaceTypeItems
    from bpy.types import bpy_struct, Area, Context, Text

from pathlib import Path

import bpy
import os


def annotations_to_dict(
    data: bpy_struct,
    recursion_depth: int = 16,
) -> dict[str, bool | int | float | str | list | dict]:
    """
    Convert datablock's properties and values to a dictionary for serialization, based
    on its annotations.

    Args:
        data (bpy_struct): Datablock to represent as dict
        recursion_depth (int): Stop after this many nested entries

    Returns:
        dict[str, bool | int | float | str | list | dict]: JSON-compatible entries
    """
    if TYPE_CHECKING:
        annotation: str
        prop: str

    if recursion_depth <= 0:
        return {}

    shelf_dict: dict[str, bool | int | float | str | list | dict] = {}
    for prop, annotation in data.__annotations__.items():
        if annotation.startswith("CollectionProperty"):
            for col in getattr(data, prop):
                col_dict = annotations_to_dict(col, recursion_depth - 1)
                shelf_dict.setdefault(prop, []).append(col_dict)  # type: ignore
            shelf_dict[prop]
        elif annotation.startswith("PointerProperty"):
            pointer = getattr(data, prop)
            shelf_dict[prop] = annotations_to_dict(pointer, recursion_depth - 1)
        else:
            shelf_dict[prop] = getattr(data, prop)

    return shelf_dict


def env_to_list(key: str) -> list[str] | None:
    """
    Returns a environment variable as list of strings, using the appropriate separater
    for the current OS.

    Args:
        key (str): Env variable name

    Returns:
        list[str] | None: Separated list of strings, if env var exists
    """
    var = os.environ.get(key)
    if var:
        return var.split(os.pathsep)


def find_area_by_type(context: Context, type: str) -> Area | None:
    """
    Finds an area that fits given area type.

    Args:
        context (Context)
        type (str): Area type to look for

    Returns:
        Area | None: First area of given type, if any exist
    """
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == type:
                return area


def find_or_create_area(
    context: Context,
    type: SpaceTypeItems,
    direction: Literal["HORIZONTAL", "VERTICAL"],
    factor: float,
) -> Area:
    """
    Finds an area that fits given area type. If none is available, creates a new area
    by splitting the current one.

    Args:
        context (Context)
        type (str): Area type to be found or created
        direction (str): Split direction
            HORIZONTAL
            VERTICAL
        factor (float): How much space newly created area will take

    Returns:
        Area: Newly created area
    """
    area = find_area_by_type(context, type)
    if area:
        return area

    area = context.area
    if not area:
        raise ValueError("No area found to split.")

    return split_area(area, type, direction, factor)


def open_script_file(filepath: str | PathLike) -> Text:
    """
    Open a file in Blender's text editor.

    Args:
        filepath (str | PathLike)

    Returns:
        Text | None
    """
    # Store existing texts snapshot
    texts = bpy.data.texts[:]

    # Open script from file path
    bpy.ops.text.open(filepath=Path(filepath).as_posix())

    # Find the newly created text datablock
    for text in bpy.data.texts:
        if text not in texts:
            return text

    raise ValueError("Couldn't find newly created text datablock.")


def same_paths(*paths: str | PathLike) -> bool:
    """
    Checks whether given paths point to the same file/folder.

    Args:
        paths (str | PathLike): Paths to compare

    Returns:
        bool: Whether all paths are the same or not
    """
    assert len(paths) > 1, "Multiple paths needed to compare"

    first_path = None
    for path in paths:
        # If path is a string, guarantee absolute path and convert to pathlib
        if isinstance(path, (str, bytes)):
            path = Path(bpy.path.abspath(path))
        elif not isinstance(path, Path):
            raise ValueError(f"Invalid path type {type(path)}")

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
    type: SpaceTypeItems,
    direction: Literal["HORIZONTAL", "VERTICAL"],
    factor: float,
) -> Area:
    """
    Splits the specified area and creates a new area of given input type.

    Args:
        area (Area): Area to split
        type (str): Area type of the newly created area
        direction (str): Split direction
            HORIZONTAL
            VERTICAL
        factor (float): How much space newly the created area will take

    Returns:
        Area: Newly created area
    """
    # Save list of areas to be able to return newly created area
    screen = area.id_data
    start_areas = screen.areas[:]  # type: ignore

    # Do split
    with bpy.context.temp_override(area=area):
        bpy.ops.screen.area_split(direction=direction, factor=factor)

    # Return the newly created area
    for area in screen.areas:  # type: ignore
        if area not in start_areas:
            area.type = type
            return area

    raise ValueError("Couldn't find new area.")
