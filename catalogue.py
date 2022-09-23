import bpy
from typing import List, Union, TypeVar


T = TypeVar("T")
BPY_REGISTER_TYPE = Union[
    bpy.types.Header,
    bpy.types.KeyingSetInfo,
    bpy.types.Menu,
    bpy.types.Operator,
    bpy.types.Panel,
    bpy.types.PropertyGroup,
    bpy.types.RenderEngine,
    bpy.types.UIList,
]


########################################################################################
# Decorators for add-on initialization
########################################################################################


def bpy_register(cls: T) -> T:
    """
    Add an object to the global catalogue to mark for registration with bpy.

    ### Use as decorator.

    Parameters:
        - cls (anything): bpy object class

    Returns:
        - anything: Unchanged object
    """
    if cls not in Catalogue.bpy_register_classes:
        Catalogue.bpy_register_classes.append(cls)

    return cls


########################################################################################
# Catalogue class
########################################################################################


class Catalogue:
    """
    Class that stores all catalogued classes and functions
    and provides methods to register or run them.
    """

    # Initialization lists
    bpy_register_classes: List[BPY_REGISTER_TYPE] = []

    # Initialization methods
    @classmethod
    def bpy_register(cls):
        """
        Loop through all collected classes and register them with bpy.
        """
        for bpy_cls in cls.bpy_register_classes:
            bpy.utils.register_class(bpy_cls)

    @classmethod
    def bpy_deregister(cls):
        """
        Loop through all collected classes and deregister them with bpy.
        """
        for bpy_cls in reversed(cls.bpy_register_classes):
            bpy.utils.unregister_class(bpy_cls)
