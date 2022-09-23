bl_info = {
    "name": "Shelf Made",
    "description": "Quick and dirty script shelf panel for Blender",
    "author": "Tristan Weis",
    "version": (1, 0, 0),
    "blender": (3, 3, 0),
    "location": "View3D",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Pipeline",
}


########################################################################################
# Imports
########################################################################################


import bpy  # nopep8
import os  # nopep8
from . import (  # nopep8
    catalogue,
    ops,
    panels,
    script,
    preferences,
)


########################################################################################
# Register functions
########################################################################################


def register():
    """
    Main registration.
    """
    # Classes registration
    catalogue.Catalogue.bpy_register()

    # Set preference class instance pointer for shortcuts
    preferences.Preferences.this = bpy.context.preferences.addons[
        __package__
    ].preferences

    # Initialize scripts
    preferences.Preferences.this.initialize_scripts()


def unregister():
    """
    De-registration. First, loop through catalogued de-registration functions.
    Then actually deregister all classes in reversed order to deactivate the
    add-on.
    """
    # Classes un-registration
    catalogue.Catalogue.bpy_deregister()
