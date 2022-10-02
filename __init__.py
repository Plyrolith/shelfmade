bl_info = {
    "name": "Shelf Made",
    "description": "Quick and dirty script shelf panel for Blender",
    "author": "Tristan Weis",
    "version": (1, 1, 0),
    "blender": (3, 3, 0),
    "location": "View3D",
    "warning": "",
    "doc_url": "https://github.com/Plyrolith/shelfmade",
    "tracker_url": "https://github.com/Plyrolith/shelfmade/issues",
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
    shelf,
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

    # Initialize scripts
    prefs = preferences.Preferences.this()
    prefs.initialize_shelves()
    prefs.clean()


def unregister():
    """
    De-registration.
    """
    # Classes un-registration
    catalogue.Catalogue.bpy_deregister()
