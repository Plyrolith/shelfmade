from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, TypeVar

    from bpy.types import (
        AddonPreferences,
        AssetShelf,
        FileHandler,
        Header,
        KeyingSetInfo,
        Menu,
        Node,
        NodeSocket,
        NodeTree,
        Operator,
        Panel,
        PropertyGroup,
        RenderEngine,
        UIList,
    )

import bpy


if TYPE_CHECKING:
    REGISTER_STRUCT = (
        Type[AddonPreferences]
        | Type[AssetShelf]
        | Type[FileHandler]
        | Type[Header]
        | Type[KeyingSetInfo]
        | Type[Menu]
        | Type[Node]
        | Type[NodeSocket]
        | Type[NodeTree]
        | Type[Operator]
        | Type[Panel]
        | Type[PropertyGroup]
        | Type[RenderEngine]
        | Type[UIList]
    )
    T = TypeVar("T", bound=REGISTER_STRUCT)


# Initialization list

bpy_register_classes: list[REGISTER_STRUCT] = []


# Decorators for add-on initialization


def bpy_register(cls: T) -> T:
    """
    Add a bpy struct class to the global catalogue to mark for registration with bpy.
    Use as decorator.

    Args:
        cls (Type[bpy_struct]): bpy struct class

    Returns:
        Type[bpy_struct]: Unchanged class
    """
    if cls not in bpy_register_classes:
        bpy_register_classes.append(cls)

    return cls


# Initialization functions


def register():
    """
    Loop through all collected classes and register them with bpy.
    """
    for cls in bpy_register_classes:
        bpy.utils.register_class(cls)


def unregister():
    """
    Loop through all collected classes and deregister them with bpy.
    """
    for cls in reversed(bpy_register_classes):
        bpy.utils.unregister_class(cls)
