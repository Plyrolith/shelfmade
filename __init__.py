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


import bpy  # nopep8


# Import all modules to jump-start classes' 'bpy_register' decorators
from . import (  # nopep8
    catalogue,
    draw,
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
    catalogue.register()

    # Initialize shelves
    prefs = preferences.Preferences.this()
    prefs.initialize_shelves()

    # Remove nonexistent shelves & scripts
    prefs.clean()

    # Add shelf menu to text editor
    bpy.types.TEXT_HT_header.append(draw.text_editor_shelf_menu)


def unregister():
    """
    De-registration.
    """
    # Remove text editor draw function
    bpy.types.TEXT_HT_header.remove(draw.text_editor_shelf_menu)

    # Classes un-registration
    catalogue.unregister()
