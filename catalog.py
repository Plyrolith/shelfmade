from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar
    from bpy.types import (
        Header,
        KeyingSetInfo,
        Menu,
        Operator,
        Panel,
        PropertyGroup,
        RenderEngine,
        UIList,
    )

import bpy


if TYPE_CHECKING:
    T = TypeVar("T")


########################################################################################
# Initialization list
########################################################################################


bpy_register_classes: list[
    Header
    | KeyingSetInfo
    | Menu
    | Operator
    | Panel
    | PropertyGroup
    | RenderEngine
    | UIList
] = []


########################################################################################
# Decorators for add-on initialization
########################################################################################


def bpy_register(cls: T) -> T:
    """
    Add an object to the global catalogue to mark for registration with bpy.

    ### Use as decorator.

    Parameters:
        - cls (Any): bpy object class

    Returns:
        - Any: Unchanged object
    """
    if cls not in bpy_register_classes:
        bpy_register_classes.append(cls)

    return cls


########################################################################################
# Initialization functions
########################################################################################


def register():
    """
    Loop through all collected classes and register them with bpy.
    """
    for bpy_cls in bpy_register_classes:
        bpy.utils.register_class(bpy_cls)


def unregister():
    """
    Loop through all collected classes and deregister them with bpy.
    """
    for bpy_cls in reversed(bpy_register_classes):
        bpy.utils.unregister_class(bpy_cls)
