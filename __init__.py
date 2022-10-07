bl_info = {
    "name": "Shelf Made",
    "description": "Quick and dirty script shelf panel for Blender",
    "author": "Tristan Weis",
    "version": (1, 1, 0),
    "blender": (3, 3, 1),
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


# Import all modules to jump-start classes' 'bpy_register' decorators
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

    # Initialize shelves
    prefs = preferences.Preferences.this()
    prefs.initialize_shelves()

    # Remove nonexistent shelves & scripts
    prefs.clean()


def unregister():
    """
    De-registration.
    """
    # Classes un-registration
    catalogue.Catalogue.bpy_deregister()
